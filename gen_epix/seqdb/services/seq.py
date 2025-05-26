import hashlib
import json
import sys
from typing import Callable, Hashable, Iterable
from uuid import UUID

import numpy as np
import scipy
from Bio.Phylo.BaseTree import Clade
from Bio.Phylo.TreeConstruction import DistanceMatrix, DistanceTreeConstructor
from scipy.cluster.hierarchy import ClusterNode

from gen_epix.fastapp import BaseUnitOfWork, CrudOperation, CrudOperationSet
from gen_epix.filter import (
    BooleanOperator,
    CompositeFilter,
    EqualsUuidFilter,
    Filter,
    UuidSetFilter,
)
from gen_epix.seqdb.domain import command, enum, exc, model
from gen_epix.seqdb.domain.service.seq import BaseSeqService


class SeqService(BaseSeqService):

    def crud(  # type: ignore
        self, cmd: command.CrudCommand
    ) -> list[model.Model] | model.Model | list[UUID] | UUID:
        """
        Override the base crud method to side effects and cascade delete
        where necessary
        """

        # TODO: remove this function once all commands are implemented
        def _get_not_implemented_message(cmd: command.CrudCommand) -> str:
            return (
                f"Command {cmd.__class__.__name__} operation {cmd.operation.value} not implemented for user with role(s) "
                + ", ".join([str(x) for x in cmd.user.roles])
            )

        def _compose_id_filter(*key_and_ids: tuple[str, set[UUID]]) -> Filter:
            return CompositeFilter(
                filters=[
                    UuidSetFilter(key=key, members=frozenset(ids))
                    for key, ids in key_and_ids
                ],
                operator=BooleanOperator.AND,
            )

        # Initialise some
        is_create = cmd.operation in CrudOperationSet.CREATE.value
        is_read = cmd.operation in CrudOperationSet.READ_OR_EXISTS.value
        is_update = cmd.operation in CrudOperationSet.UPDATE.value
        is_delete = cmd.operation in CrudOperationSet.DELETE.value
        access_filter = None

        # Start unit of work and execute all within this scope
        with self.repository.uow() as uow:

            if isinstance(cmd, command.AlleleProfileCrudCommand):
                if is_create:
                    # Calculate all distances for these allele profiles between themselves and with all stored allele profiles
                    allele_profiles: list[model.AlleleProfile] = cmd.get_objs()
                    self._calculate_allele_profile_distances(uow, allele_profiles)

                elif is_read:
                    # Nothing to do extra
                    pass
                elif is_update:
                    # May only change the representation format, not the profile itself
                    raise NotImplementedError(_get_not_implemented_message(cmd))
                elif is_delete:
                    # Delete all distances for these allele profiles as well
                    raise NotImplementedError(_get_not_implemented_message(cmd))
                else:
                    raise NotImplementedError(_get_not_implemented_message(cmd))

        return super().crud(cmd)

    def _calculate_allele_profile_distances(
        self, uow: BaseUnitOfWork, allele_profiles: list[model.AlleleProfile]
    ) -> list[model.SeqDistance]:
        """
        Calculate all distances for these allele profiles between themselves and with
        all stored allele profiles, for all distance protocols that are applicable to
        the locus set of the allele profiles.
        """
        locus_set_ids = {x.locus_set_id for x in allele_profiles}
        cmd = command.SeqDistanceProtocolCrudCommand(
            user=None,
            operation=CrudOperation.READ_ALL,
            query_filter=UuidSetFilter(key="locus_set_id", members=locus_set_ids),
        )
        seq_distance_protocols = self.crud_repository(uow, cmd)
        seq_distances = self.calculate_pairwise_allele_profile_distances(
            seq_distance_protocols, allele_profiles
        )
        # TODO: calculate distances with all stored allele profiles
        # TODO: store/update distances
        # raise NotImplementedError()
        return seq_distances

    def retrieve_phylogenetic_tree(
        self, cmd: command.RetrievePhylogeneticTreeCommand
    ) -> model.PhylogeneticTree | None:
        # profiler = pyinstrument.Profiler(async_mode="enabled")
        # profiler.start()

        user_id = cmd.user.id if cmd.user else None
        seq_ids = cmd.seq_ids
        tree_algorithm = cmd.tree_algorithm
        seq_distance_protocol_id = cmd.seq_distance_protocol_id
        if len(set(seq_ids)) != len(seq_ids):
            raise exc.InvalidArgumentsError("seq_ids must be unique")
        leaf_names = cmd.leaf_names if cmd.leaf_names else [str(x) for x in seq_ids]

        # Retrieve genetic distance protocol
        with self.repository.uow() as uow:
            seq_distance_protocol: model.SeqDistanceProtocol = self.repository.crud(  # type: ignore[assignment]
                uow,
                user_id,
                model.SeqDistanceProtocol,
                None,
                seq_distance_protocol_id,
                CrudOperation.READ_ONE,
            )

        # Special case: 0 or 1 sequences
        if len(seq_ids) < 2:
            return model.PhylogeneticTree(
                id=self.generate_id(),
                tree_algorithm=tree_algorithm,
                seq_distance_protocol_id=seq_distance_protocol_id,
                seq_ids=seq_ids,
                leaf_names=leaf_names,
                newick_repr=f"({leaf_names[0]});" if seq_ids else "();",
            )

        # Retrieve distance matrix
        if tree_algorithm in enum.TreeAlgorithmSet.DISTANCE_BASED.value:
            with self.repository.uow() as uow:
                seq_distances_: list[model.SeqDistance] = self.repository.crud(  # type: ignore[assignment]
                    uow,
                    user_id,
                    model.SeqDistance,
                    None,
                    None,
                    CrudOperation.READ_ALL,
                    filter=CompositeFilter(
                        filters=[
                            UuidSetFilter(key="seq_id", members=frozenset(seq_ids)),
                            EqualsUuidFilter(
                                key="seq_distance_protocol_id",
                                value=seq_distance_protocol_id,
                            ),
                        ],
                        operator=BooleanOperator.AND,
                    ),
                )
                seq_distances = {x.seq_id: x for x in seq_distances_}
            max_stored_distance = seq_distance_protocol.max_stored_distance
            # Calculate condensed distance matrix
            tree_seq_distances_ = [
                seq_distances[x] for x in seq_ids if x in seq_distances
            ]
            tree_leaf_names = [
                x for x, y in zip(leaf_names, seq_ids) if y in seq_distances
            ]
            tree_seq_ids = [x.seq_id for x in tree_seq_distances_]
            tree_seq_ids_index_map = {x: i for i, x in enumerate(tree_seq_ids)}
            str_seq_profile_id_index_map = {
                str(
                    x.allele_profile_id
                    if x.allele_profile_id
                    else (x.snp_profile_id if x.snp_profile_id else x.kmer_profile_id)
                ): tree_seq_ids_index_map[x.seq_id]
                for x in seq_distances.values()
            }
            n_seqs_with_distances = len(tree_seq_ids)
            condensed_distance_matrix = max_stored_distance * np.ones(
                (int(n_seqs_with_distances * (n_seqs_with_distances - 1) / 2),),
                dtype=float,
            )

            def _get_condensed_distance_matrix_index(i: int, j: int, n: int) -> int:
                if i < j:
                    i, j = j, i
                return n * j - j * (j + 1) // 2 + i - 1 - j

            for i, seq_distance in enumerate(tree_seq_distances_):
                if (
                    seq_distance.distance_format
                    != enum.SeqDistanceFormat.SEQ_ID_DISTANCE_DICT
                ):
                    distances = json.loads(seq_distance.distances)
                    for str_seq_profile_id, distance in distances.items():
                        if str_seq_profile_id not in str_seq_profile_id_index_map:
                            # Distance to a sequence not in the list of seq_ids
                            continue
                        j = str_seq_profile_id_index_map[str_seq_profile_id]
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
                        "Only distance format SEQ_ID_DISTANCE_DICT is supported"
                    )
            # Handle sequences with no stored distances
            if len(tree_seq_ids) < 2:
                return model.PhylogeneticTree(
                    id=self.generate_id(),
                    tree_algorithm=tree_algorithm,
                    seq_distance_protocol_id=seq_distance_protocol_id,
                    seq_ids=seq_ids,
                    leaf_names=leaf_names,
                    newick_repr=f"({tree_leaf_names[0]});" if tree_seq_ids else "();",
                )
            # Calculate tree
            # Increase recursion limit to allow for larger trees
            sys_recursion_limit = sys.getrecursionlimit()
            sys.setrecursionlimit(sys_recursion_limit + len(tree_seq_ids) + 1)
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
                    newick_repr = SeqService._get_newick_repr_recursion(
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
                    distance_tree_constructor = DistanceTreeConstructor()
                    bio_distance_matrix = DistanceMatrix(names, lower_triangle)
                    tree = distance_tree_constructor.nj(bio_distance_matrix)
                    # Neighbour joining can produce negative branch lengths
                    # https://en.wikipedia.org/wiki/Neighbor_joining
                    # https://www.researchgate.net/post/How-to-correct-negative-branches-from-neighbor-joining-method
                    # These are corrected here by adding the single negative minimum branch length to all branches
                    SeqService._correct_nj_tree_negative_branch_lengths_recursion(
                        tree.clade
                    )
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
            id=self.generate_id(),
            tree_algorithm=tree_algorithm,
            seq_distance_protocol_id=seq_distance_protocol_id,
            seq_ids=seq_ids,
            leaf_names=leaf_names,
            newick_repr=newick_repr,
        )
        # profiler.stop()
        # profiler.write_html(
        #     "./test/data/output/profile_retrieve_phylogenetic_tree.html"
        # )
        return phylogenetic_tree

    def retrieve_allele_profile(
        self,
        cmd: command.RetrieveCompleteAlleleProfileCommand,
    ) -> model.CompleteAlleleProfile | list[model.CompleteAlleleProfile]:
        raise NotImplementedError()

    def retrieve_snp_profile(
        self, cmd: command.RetrieveCompleteSnpProfileCommand
    ) -> model.CompleteSnpProfile | list[model.CompleteSnpProfile]:
        raise NotImplementedError()

    def retrieve_contig(
        self, cmd: command.RetrieveCompleteContigCommand
    ) -> model.CompleteContig | list[model.CompleteContig]:
        raise NotImplementedError()

    def retrieve_multiple_alignment(
        self, cmd: command.RetrieveMultipleAlignmentCommand
    ) -> model.MultipleAlignment | list[model.MultipleAlignment]:
        raise NotImplementedError()

    def retrieve_sample(
        self, cmd: command.RetrieveCompleteSampleCommand
    ) -> model.CompleteSample | list[model.CompleteSample]:
        raise NotImplementedError()

    def retrieve_seq(
        self, cmd: command.RetrieveCompleteSeqCommand
    ) -> model.CompleteSeq | list[model.CompleteSeq]:
        raise NotImplementedError()

    @staticmethod
    def calculate_pairwise_allele_profile_distances(
        seq_distance_protocols: Iterable[model.SeqDistanceProtocol],
        allele_profiles: Iterable[model.AlleleProfile],
    ) -> list[model.SeqDistance]:
        """
        Calculate all distances for a set of allele profiles between themselves for all
        the given distance protocols.
        """
        seq_distances: list[model.SeqDistance] = []
        # Go over each distance protocol
        for seq_distance_protocol in seq_distance_protocols:
            assert seq_distance_protocol.id is not None
            locus_set_id = seq_distance_protocol.locus_set_id
            if locus_set_id is None:
                raise exc.InvalidArgumentsError(
                    "SeqDistanceProtocol must have a locus_set_id"
                )
            # Get distance calculation function
            if (
                seq_distance_protocol.seq_distance_protocol_type
                == enum.SeqDistanceProtocolType.ALLELE_HAMMING
            ):
                calculate_distance = SeqService.calculate_hamming_distance
            else:
                raise NotImplementedError()
            # Select only allele profiles for this locus set that are of usable quality
            curr_allele_profiles: list[model.AlleleProfile] = [
                x
                for x in allele_profiles
                if x.locus_set_id == locus_set_id
                and x.quality
                and x.quality.is_usable()
            ]
            # Convert allele_profile from json to object
            allele_profile_allele_ids = [
                json.loads(x.allele_profile) for x in curr_allele_profiles
            ]
            allele_profile_str_seq_ids = [str(x.seq_id) for x in curr_allele_profiles]
            # Go over each unique pair of allele profiles
            curr_seq_distances: dict[int, dict[str, float]] = {
                i: dict() for i in range(len(curr_allele_profiles))
            }
            for i, allele_profile1 in enumerate(curr_allele_profiles):
                # First allele profile
                allele_profile_format1 = allele_profile1.allele_profile_format
                allele_ids1 = allele_profile_allele_ids[i]
                seq_id1 = allele_profile_str_seq_ids[i]
                for j in range(i + 1, len(curr_allele_profiles)):
                    # Second allele profile
                    allele_profile2 = curr_allele_profiles[j]
                    allele_profile_format2 = allele_profile2.allele_profile_format
                    allele_ids2 = allele_profile_allele_ids[j]
                    seq_id2 = allele_profile_str_seq_ids[j]
                    # Calculate distance depending on format of each allele profile
                    distance = SeqService.calculate_allele_profile_distance(
                        calculate_distance,
                        allele_profile_format1,
                        allele_ids1,
                        allele_profile_format2,
                        allele_ids2,
                    )
                    # Keep only distances up to the maximum
                    if distance > seq_distance_protocol.max_stored_distance:
                        continue
                    # Add to seq_distances
                    curr_seq_distances[i][seq_id2] = distance
                    curr_seq_distances[j][seq_id1] = distance

            # Create SeqDistance objects from distances
            for i, allele_profile in enumerate(curr_allele_profiles):
                # Calculate SeqDistance.id as 128 bit hash of seq_id, so that it is always the same
                seq_distance_id = UUID(
                    bytes=hashlib.md5(allele_profile_str_seq_ids[i].encode()).digest()
                )
                # Create seq_distance and add to dict_db
                seq_distance = model.SeqDistance(
                    id=seq_distance_id,
                    seq_id=allele_profile.seq_id,
                    seq_distance_protocol_id=seq_distance_protocol.id,
                    allele_profile_id=allele_profile.id,
                    distance_format=enum.SeqDistanceFormat.SEQ_ID_DISTANCE_DICT,
                    distances=json.dumps(curr_seq_distances[i]),
                )
                seq_distances.append(seq_distance)

        return seq_distances

    @staticmethod
    def calculate_allele_profile_distance(
        calculate_distance: Callable[[list[Hashable], list[Hashable]], float],
        allele_profile_format1: enum.AlleleProfileFormat,
        allele_ids1: list[Hashable],
        allele_profile_format2: enum.AlleleProfileFormat,
        allele_ids2: list[Hashable],
    ) -> float:
        """
        Calculate the distance between two allele profiles
        """
        if allele_profile_format1 == enum.AlleleProfileFormat.SORTED_ALLELE_IDS:
            if allele_profile_format2 == enum.AlleleProfileFormat.SORTED_ALLELE_IDS:
                distance = calculate_distance(allele_ids1, allele_ids2)
            else:
                raise NotImplementedError()
        else:
            raise NotImplementedError()
        return distance

    @staticmethod
    def calculate_hamming_distance(ids1: list[Hashable], ids2: list[Hashable]) -> float:
        """
        Calculate Hamming distance between allele or snp profiles: per locus, add 1
        to the distance if the alleles are different. In case one of the two loci are
        missing, the distance is not increased and neither is it if both are missing
        """
        return float(
            sum(
                1
                for x, y in zip(ids1, ids2)
                if x != y and x is not None and y is not None
            )
        )

    @staticmethod
    def _correct_nj_tree_negative_branch_lengths_recursion(clade: Clade) -> None:
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
            SeqService._correct_nj_tree_negative_branch_lengths_recursion(subclade)

    @staticmethod
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
        newick = SeqService._get_newick_repr_recursion(
            node.get_left(),
            node.dist,
            leaf_names,
            newick=newick,
        )
        newick = SeqService._get_newick_repr_recursion(
            node.get_right(),
            node.dist,
            leaf_names,
            newick=f",{newick}",
        )
        newick = f"({newick}"
        return newick
