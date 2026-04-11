import json
import sys
from typing import Any, cast
from uuid import UUID

import numpy as np
import scipy  # type: ignore[import-untyped]
from Bio.Phylo.TreeConstruction import (  # type: ignore[import-untyped]
    DistanceMatrix,
    DistanceTreeConstructor,
)
from scipy.cluster.hierarchy import ClusterNode  # type: ignore[import-untyped]

from gen_epix.commondb.domain import exc
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.filter.composite import CompositeFilter
from gen_epix.filter.enum import LogicalOperator
from gen_epix.filter.equals_uuid import EqualsUuidFilter
from gen_epix.filter.uuid_set import UuidSetFilter
from gen_epix.seqdb.domain import command, enum, model
from gen_epix.seqdb.domain.repository.seq import BaseSeqRepository
from gen_epix.seqdb.domain.service.seq import BaseSeqService


def seq_service_calculate_phylogenetic_tree(
    self: BaseSeqService,
    cmd: command.CalculatePhylogeneticTreeCommand,
) -> model.PhylogeneticTree:

    # profiler = pyinstrument.Profiler(async_mode="enabled")
    # profiler.start()

    user_id = cmd.user.id if cmd.user else None
    seq_profile_ids = cmd.seq_profile_ids
    tree_algorithm = cmd.tree_algorithm
    protocol_id = cmd.protocol_id
    if len(set(seq_profile_ids)) != len(seq_profile_ids):
        raise exc.InvalidArgumentsError("profile_ids must be unique")
    leaf_names = cmd.leaf_names if cmd.leaf_names else [str(x) for x in seq_profile_ids]

    # Handle transaction
    repository: BaseSeqRepository = self.repository  # type: ignore[assignment]
    seq_distances: list[model.SeqDistance]
    with repository.uow() as uow:
        # Filter provided seq_profile_ids by quality control result
        seq_profile_ids: list[UUID] = (  # type: ignore[no-redef]
            repository.filter_seq_profiles_by_quality(
                uow,
                seq_profile_ids=seq_profile_ids,
                allowed_qc_results=cast(Any, cmd).allowed_qc_results,
            )
        )

        # Retrieve genetic distance protocol
        protocol: model.Protocol = repository.crud(  # type: ignore[assignment]
            uow,
            user_id,
            model.Protocol,
            CrudOperation.READ_ONE,
            obj_ids=protocol_id,
        )

        # Special case: 0 or 1 sequences
        if len(seq_profile_ids) < 2:
            return model.PhylogeneticTree(
                id=self.generate_id(),  # type: ignore[arg-type]
                tree_algorithm=tree_algorithm,
                protocol_id=protocol_id,
                profile_ids=seq_profile_ids,
                leaf_names=leaf_names,
                newick_repr=f"({leaf_names[0]});" if seq_profile_ids else "();",
            )

        # Retrieve distance matrix
        if tree_algorithm in enum.TreeAlgorithmSet.DISTANCE_BASED.value:
            seq_distances = repository.crud(  # type: ignore[assignment]
                uow,
                user_id,
                model.SeqDistance,
                CrudOperation.READ_ALL,
                filter=CompositeFilter(
                    filters=[
                        UuidSetFilter(
                            key="seq_profile_id", members=frozenset(seq_profile_ids)
                        ),
                        EqualsUuidFilter(
                            key="protocol_id",
                            value=protocol_id,
                        ),
                    ],
                    operator=LogicalOperator.AND,
                ),
            )
        else:
            raise exc.InvalidArgumentsError(
                f"{tree_algorithm.value} tree algorithm not yet implemented"
            )

    # Stop transaction here, releasing resources, since the rest of the operations are in-memory and do not require database access. This also allows for better parallelisation if the tree calculation would be made asynchronous in the future, without the need to keep the transaction open for the entire duration of the tree calculation.
    if tree_algorithm in enum.TreeAlgorithmSet.DISTANCE_BASED.value:
        seq_distance_map = {x.seq_profile_id: x for x in seq_distances}
        max_stored_distance = protocol.max_stored_distance
        # Calculate condensed distance matrix
        tree_seq_distances = [
            seq_distance_map[x] for x in seq_profile_ids if x in seq_distance_map
        ]
        tree_leaf_names = [
            x for x, y in zip(leaf_names, seq_profile_ids) if y in seq_distance_map
        ]
        tree_profile_ids = [x.seq_profile_id for x in tree_seq_distances]
        tree_profile_id_idx_map = {str(x): i for i, x in enumerate(tree_profile_ids)}
        n_seqs_with_distances = len(tree_profile_ids)
        condensed_distance_matrix = max_stored_distance * np.ones(
            (int(n_seqs_with_distances * (n_seqs_with_distances - 1) / 2),),
            dtype=float,
        )

        def _get_condensed_distance_matrix_index(i: int, j: int, n: int) -> int:
            if i < j:
                i, j = j, i
            return n * j - j * (j + 1) // 2 + i - 1 - j

        for i, seq_distance in enumerate(tree_seq_distances):
            if seq_distance.format == enum.SeqDistanceFormat.PROFILE_DISTANCE_MAP:
                distances = json.loads(seq_distance.content)
                for profile_id_str, distance in distances.items():
                    if profile_id_str not in tree_profile_id_idx_map:
                        # Distance to a sequence not in the list of seq_ids
                        continue
                    j = tree_profile_id_idx_map[profile_id_str]
                    if distance > max_stored_distance:
                        # Go only up to max_stored_distance in distance matrix,
                        # even if this actual stored distance is larger, e.g.
                        # because the max_stored_distance was higher in the past
                        # TODO: this should be parameterised, so that such higher
                        # distances would nonetheless be used
                        distance = max_stored_distance
                    k = _get_condensed_distance_matrix_index(
                        i, j, n_seqs_with_distances
                    )
                    condensed_distance_matrix[k] = distance
            else:
                raise exc.InvalidArgumentsError(
                    f"Distance format {seq_distance.format.name} is not supported"
                )

        # Handle sequences with no stored distances
        if len(tree_profile_ids) < 2:
            return model.PhylogeneticTree(
                id=self.generate_id(),  # type: ignore[arg-type]
                tree_algorithm=tree_algorithm,
                protocol_id=protocol_id,
                profile_ids=seq_profile_ids,
                leaf_names=leaf_names,
                newick_repr=(f"({tree_leaf_names[0]});" if tree_profile_ids else "();"),
            )

        # Calculate tree
        # Increase recursion limit to allow for larger trees
        sys_recursion_limit = sys.getrecursionlimit()
        sys.setrecursionlimit(sys_recursion_limit + len(tree_profile_ids) + 1)
        scipy_tree_algorithm_code_map = {
            enum.TreeAlgorithm.SLINK: "single",
            enum.TreeAlgorithm.UPGMA: "average",
        }
        try:
            if tree_algorithm in scipy_tree_algorithm_code_map:
                linkage_result = scipy.cluster.hierarchy.linkage(
                    condensed_distance_matrix,
                    scipy_tree_algorithm_code_map[tree_algorithm],
                )
                tree = scipy.cluster.hierarchy.to_tree(linkage_result, False)
                newick_repr = _get_newick_repr_recursion(
                    tree, tree.dist, tree_leaf_names
                )
            elif tree_algorithm == enum.TreeAlgorithm.NJ:
                # TODO: convert condensed distance matrix directly to lower triangle
                distance_matrix = scipy.spatial.distance.squareform(
                    condensed_distance_matrix
                )
                lower_triangle = []
                for i, x in enumerate(distance_matrix):
                    lower_triangle.append(list(x[: i + 1]))
                names = [str(x) for x in tree_leaf_names]
                distance_tree_constructor = DistanceTreeConstructor()  # type: ignore[no-untyped-call]
                bio_distance_matrix = DistanceMatrix(  # type: ignore[no-untyped-call]
                    names,
                    lower_triangle,
                )
                tree = distance_tree_constructor.nj(bio_distance_matrix)  # type: ignore[no-untyped-call]
                # Neighbour joining can produce negative branch lengths
                # https://en.wikipedia.org/wiki/Neighbor_joining
                # https://www.researchgate.net/post/How-to-correct-negative-branches-from-neighbor-joining-method
                # These are corrected here by adding the single negative minimum branch length to all branches
                _correct_nj_tree_negative_branch_lengths_recursion(tree.clade)
                newick_repr = tree.format("newick")
            else:
                raise exc.InvalidArgumentsError(
                    f"{tree_algorithm.value} tree algorithm not yet implemented"
                )
        finally:
            # Always set recursion limit back to allow for larger trees
            sys.setrecursionlimit(sys_recursion_limit)
    else:
        raise exc.InvalidArgumentsError(
            f"{tree_algorithm.value} tree algorithm not yet implemented"
        )
    phylogenetic_tree = model.PhylogeneticTree(
        id=self.generate_id(),  # type: ignore[arg-type]
        tree_algorithm=tree_algorithm,
        protocol_id=protocol_id,
        profile_ids=seq_profile_ids,
        leaf_names=leaf_names,
        newick_repr=newick_repr,
    )
    # profiler.stop()
    # profiler.write_html(
    #     "./test/output/profile_calculate_phylogenetic_tree.html"
    # )
    return phylogenetic_tree


def _correct_nj_tree_negative_branch_lengths_recursion(clade: Any) -> None:
    """
    Recursively update negative branch lengths by adding the negative branch
    length to all siblings. Only one sibling may have a negative branch length.
    """

    # TODO: check if this is correct. Non-terminal branches may have their length
    # updated (extended). As a result their distance to other clades also
    # increases, even if the distance to the sibling that had the negative branch
    # length remains identical.
    if clade.is_terminal():
        return
    min_branch_length = 0
    for subclade in clade.clades:
        if subclade.branch_length < 0:
            if min_branch_length < 0:
                raise ValueError("More than one negative branch length in a clade")
            min_branch_length = subclade.branch_length
    if min_branch_length < 0:
        for subclade in clade.clades:
            subclade.branch_length -= min_branch_length
    for subclade in clade.clades:
        _correct_nj_tree_negative_branch_lengths_recursion(subclade)


def _get_newick_repr_recursion(
    node: ClusterNode, parent_dist: float, leaf_names: list[str], newick: str = ""
) -> str:
    """
    Convert sciply.cluster.hierarchy.to_tree()-output to Newick format.

    :param node: output of sciply.cluster.hierarchy.to_tree()
    :param parent_dist: output of sciply.cluster.hierarchy.to_tree().dist
    :param leaf_names: list of leaf names
    :param newick: leave empty, this variable is used in recursion.
    :returns: tree in Newick format
    """
    if node.is_leaf():
        return f"{leaf_names[node.id]}:{parent_dist - node.dist:.2f}{newick}"
    if newick:
        newick = f"):{parent_dist - node.dist:.2f}{newick}"
    else:
        newick = ");"
    newick = _get_newick_repr_recursion(
        cast(ClusterNode, node.get_left()),
        node.dist,
        leaf_names,
        newick=newick,
    )
    newick = _get_newick_repr_recursion(
        cast(ClusterNode, node.get_right()),
        node.dist,
        leaf_names,
        newick=f",{newick}",
    )
    newick = f"({newick}"
    return newick
