import hashlib
import json
import sys
from collections.abc import Callable, Hashable, Iterable
from uuid import UUID

import numpy as np
import scipy
from Bio.Phylo.BaseTree import Clade
from Bio.Phylo.TreeConstruction import DistanceMatrix, DistanceTreeConstructor
from scipy.cluster.hierarchy import ClusterNode

from gen_epix.fastapp import BaseUnitOfWork, CrudOperation
from gen_epix.filter import (
    CompositeFilter,
    EqualsUuidFilter,
    Filter,
    LogicalOperator,
    UuidSetFilter,
)
from gen_epix.seqdb.domain import command, enum, exc, model
from gen_epix.seqdb.domain.repository import BaseSeqRepository
from gen_epix.seqdb.domain.service import BaseSeqService
from gen_epix.seqdb.services.seq.calculate_seq_distance import (
    seq_service_calculate_seq_distances_for_new_profiles,
)
from gen_epix.seqdb.services.seq.crud_allele import seq_service_crud_allele
from gen_epix.seqdb.services.seq.crud_allele_profile import (
    seq_service_crud_allele_profile,
)
from gen_epix.seqdb.services.seq.crud_allele_profile_identifier import (
    seq_service_crud_allele_profile_identifier,
)
from gen_epix.seqdb.services.seq.crud_ast_measurement import (
    seq_service_crud_ast_measurement,
)
from gen_epix.seqdb.services.seq.crud_ast_prediction import (
    seq_service_crud_ast_prediction,
)
from gen_epix.seqdb.services.seq.crud_file import seq_service_crud_file
from gen_epix.seqdb.services.seq.crud_kmer_profile import seq_service_crud_kmer_profile
from gen_epix.seqdb.services.seq.crud_kmer_profile_identifier import (
    seq_service_crud_kmer_profile_identifier,
)
from gen_epix.seqdb.services.seq.crud_locus import seq_service_crud_locus
from gen_epix.seqdb.services.seq.crud_locus_code_map import (
    seq_service_crud_locus_code_map,
)
from gen_epix.seqdb.services.seq.crud_locus_profile import (
    seq_service_crud_locus_profile,
)
from gen_epix.seqdb.services.seq.crud_locus_profile_identifier import (
    seq_service_crud_locus_profile_identifier,
)
from gen_epix.seqdb.services.seq.crud_locus_set import seq_service_crud_locus_set
from gen_epix.seqdb.services.seq.crud_mlva_profile import seq_service_crud_mlva_profile
from gen_epix.seqdb.services.seq.crud_mlva_profile_identifier import (
    seq_service_crud_mlva_profile_identifier,
)
from gen_epix.seqdb.services.seq.crud_pcr_measurement import (
    seq_service_crud_pcr_measurement,
)
from gen_epix.seqdb.services.seq.crud_protocol import seq_service_crud_protocol
from gen_epix.seqdb.services.seq.crud_read_set import seq_service_crud_read_set
from gen_epix.seqdb.services.seq.crud_read_set_identifier import (
    seq_service_crud_read_set_identifier,
)
from gen_epix.seqdb.services.seq.crud_ref_allele import seq_service_crud_ref_allele
from gen_epix.seqdb.services.seq.crud_ref_seq import seq_service_crud_ref_seq
from gen_epix.seqdb.services.seq.crud_sample import seq_service_crud_sample
from gen_epix.seqdb.services.seq.crud_sample_data_collection_link import (
    seq_service_crud_sample_data_collection_link,
)
from gen_epix.seqdb.services.seq.crud_sample_identifier import (
    seq_service_crud_sample_identifier,
)
from gen_epix.seqdb.services.seq.crud_seq import seq_service_crud_seq
from gen_epix.seqdb.services.seq.crud_seq_category import seq_service_crud_seq_category
from gen_epix.seqdb.services.seq.crud_seq_category_set import (
    seq_service_crud_seq_category_set,
)
from gen_epix.seqdb.services.seq.crud_seq_classification import (
    seq_service_crud_seq_classification,
)
from gen_epix.seqdb.services.seq.crud_seq_distance import seq_service_crud_seq_distance
from gen_epix.seqdb.services.seq.crud_seq_identifier import (
    seq_service_crud_seq_identifier,
)
from gen_epix.seqdb.services.seq.crud_seq_taxonomy import seq_service_crud_seq_taxonomy
from gen_epix.seqdb.services.seq.crud_snp_profile import seq_service_crud_snp_profile
from gen_epix.seqdb.services.seq.crud_snp_profile_identifier import (
    seq_service_crud_snp_profile_identifier,
)
from gen_epix.seqdb.services.seq.crud_taxon import seq_service_crud_taxon
from gen_epix.seqdb.services.seq.crud_taxon_set import seq_service_crud_taxon_set
from gen_epix.seqdb.services.seq.crud_taxon_set_member import (
    seq_service_crud_taxon_set_member,
)
from gen_epix.seqdb.services.seq.crud_tree_algorithm import (
    seq_service_crud_tree_algorithm,
)
from gen_epix.seqdb.services.seq.crud_tree_algorithm_class import (
    seq_service_crud_tree_algorithm_class,
)
from gen_epix.seqdb.services.seq.upload import seq_service_upload_samples


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
                operator=LogicalOperator.AND,
            )

        # Start unit of work and execute all within this scope
        with self.repository.uow() as uow:

            if isinstance(cmd, command.AlleleProfileCrudCommand):
                if cmd.is_create():
                    # Calculate all distances for these allele profiles between themselves and with all stored allele profiles
                    allele_profiles: list[model.AlleleProfile] = cmd.get_objs()
                    self._calculate_allele_profile_distances(uow, allele_profiles)

                elif cmd.is_read():
                    # Nothing to do extra
                    pass
                elif cmd.is_update():
                    # May only change the representation format, not the profile itself
                    raise NotImplementedError(_get_not_implemented_message(cmd))
                elif cmd.is_delete():
                    # Delete all distances for these allele profiles as well
                    raise NotImplementedError(_get_not_implemented_message(cmd))
                else:
                    raise NotImplementedError(_get_not_implemented_message(cmd))

        return super().crud(cmd)

    def upload_samples(
        self,
        cmd: command.UploadSamplesCommand,
    ) -> model.SampleBatchUploadResult:
        return seq_service_upload_samples(self, cmd)

    def retrieve_phylogenetic_tree(
        self, cmd: command.RetrievePhylogeneticTreeCommand
    ) -> model.PhylogeneticTree | None:
        # profiler = pyinstrument.Profiler(async_mode="enabled")
        # profiler.start()

        user_id = cmd.user.id if cmd.user else None
        profile_ids = cmd.profile_ids
        tree_algorithm = cmd.tree_algorithm
        protocol_id = cmd.protocol_id
        if len(set(profile_ids)) != len(profile_ids):
            raise exc.InvalidArgumentsError("profile_ids must be unique")
        leaf_names = cmd.leaf_names if cmd.leaf_names else [str(x) for x in profile_ids]

        # Retrieve genetic distance protocol
        with self.repository.uow() as uow:
            protocol: model.Protocol = self.repository.crud(  # type: ignore[assignment]
                uow,
                user_id,
                model.Protocol,
                None,
                protocol_id,
                CrudOperation.READ_ONE,
            )

        # Special case: 0 or 1 sequences
        if len(profile_ids) < 2:
            return model.PhylogeneticTree(
                id=self.generate_id(),  # type: ignore[arg-type]
                tree_algorithm=tree_algorithm,
                protocol_id=protocol_id,
                profile_ids=profile_ids,
                leaf_names=leaf_names,
                newick_repr=f"({leaf_names[0]});" if profile_ids else "();",
            )

        # Retrieve distance matrix
        if tree_algorithm in enum.TreeAlgorithmSet.DISTANCE_BASED.value:
            with self.repository.uow() as uow:
                seq_distances: list[model.SeqDistance] = self.repository.crud(  # type: ignore[assignment]
                    uow,
                    user_id,
                    model.SeqDistance,
                    None,
                    None,
                    CrudOperation.READ_ALL,
                    filter=CompositeFilter(
                        filters=[
                            UuidSetFilter(
                                key="profile_id", members=frozenset(profile_ids)
                            ),
                            EqualsUuidFilter(
                                key="protocol_id",
                                value=protocol_id,
                            ),
                        ],
                        operator=LogicalOperator.AND,
                    ),
                )
                seq_distance_map = {x.profile_id: x for x in seq_distances}
            max_stored_distance = protocol.max_stored_distance
            # Calculate condensed distance matrix
            tree_seq_distances = [
                seq_distance_map[x] for x in profile_ids if x in seq_distance_map
            ]
            tree_leaf_names = [
                x for x, y in zip(leaf_names, profile_ids) if y in seq_distance_map
            ]
            tree_profile_ids = [x.profile_id for x in tree_seq_distances]
            tree_profile_id_idx_map = {
                str(x): i for i, x in enumerate(tree_profile_ids)
            }
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
                if (
                    seq_distance.distance_format
                    == enum.SeqDistanceFormat.PROFILE_DISTANCE_MAP
                ):
                    distances = json.loads(seq_distance.distances)
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
                        f"Distance format {seq_distance.distance_format.value} is not supported"
                    )
            # Handle sequences with no stored distances
            if len(tree_profile_ids) < 2:
                return model.PhylogeneticTree(
                    id=self.generate_id(),  # type: ignore[arg-type]
                    tree_algorithm=tree_algorithm,
                    protocol_id=protocol_id,
                    profile_ids=profile_ids,
                    leaf_names=leaf_names,
                    newick_repr=(
                        f"({tree_leaf_names[0]});" if tree_profile_ids else "();"
                    ),
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
            id=self.generate_id(),  # type: ignore[arg-type]
            tree_algorithm=tree_algorithm,
            protocol_id=protocol_id,
            profile_ids=profile_ids,
            leaf_names=leaf_names,
            newick_repr=newick_repr,
        )
        # profiler.stop()
        # profiler.write_html(
        #     "./test/output/profile_retrieve_phylogenetic_tree.html"
        # )
        return phylogenetic_tree

    def retrieve_samples(
        self, cmd: command.RetrieveSamplesCommand
    ) -> list[model.SampleForUpload]:
        raise NotImplementedError()

    def retrieve_seq_fasta(self, cmd: command.RetrieveSeqFastaCommand) -> Iterable[str]:
        wrap = cmd.wrap or cmd.model_fields["wrap"].default
        self.repository: BaseSeqRepository
        with self.repository.uow() as uow:
            for seq_id, contigs in self.repository.retrieve_seq_fasta(uow, cmd.seq_ids):
                for contig_seq_hash, raw_seq in contigs:
                    header = f">{seq_id}:{contig_seq_hash}\n"
                    if not wrap:
                        yield f"{header}{raw_seq}\n"
                    seq_length = len(raw_seq)
                    n_chunks = (seq_length // wrap) + (seq_length % wrap > 0)
                    yield header + "\n".join(
                        raw_seq[i * wrap : min((i + 1) * wrap, seq_length)]
                        for i in range(n_chunks)
                    )

    def _calculate_allele_profile_distances(
        self, uow: BaseUnitOfWork, allele_profiles: list[model.AlleleProfile]
    ) -> list[model.SeqDistance]:
        """
        Calculate all distances for these allele profiles between themselves and with
        all stored allele profiles, for all distance protocols that are applicable to
        the locus set of the allele profiles.
        """
        locus_set_ids = {x.locus_set_id for x in allele_profiles}
        cmd = command.ProtocolCrudCommand(
            user=None,
            operation=CrudOperation.READ_ALL,
            query_filter=UuidSetFilter(key="locus_set_id", members=locus_set_ids),
        )
        protocols = self.crud_repository(uow, cmd)
        seq_distances = self.calculate_pairwise_allele_profile_distances(
            protocols, allele_profiles
        )
        # TODO: calculate distances with all stored allele profiles
        # TODO: store/update distances
        # raise NotImplementedError()
        return seq_distances

    @staticmethod
    def calculate_pairwise_allele_profile_distances(
        protocols: Iterable[model.Protocol],
        allele_profiles: Iterable[model.AlleleProfile],
    ) -> list[model.SeqDistance]:
        """
        Calculate all distances for a set of allele profiles between themselves for all
        the given distance protocols.
        """
        seq_distances: list[model.SeqDistance] = []
        # Go over each distance protocol
        for protocol in protocols:
            assert protocol.id is not None
            locus_set_id = protocol.locus_set_id
            if locus_set_id is None:
                raise exc.InvalidArgumentsError("Protocol must have a locus_set_id")
            # Get distance calculation function
            if protocol.seq_distance_type == enum.SeqDistanceType.ALLELE_HAMMING:
                calculate_distance = SeqService.calculate_hamming_distance
            else:
                raise NotImplementedError()
            # Select only allele profiles for this locus set that are of usable quality
            curr_allele_profiles: list[model.AlleleProfile] = [
                x
                for x in allele_profiles
                if x.locus_set_id == locus_set_id
                and x.qc_result
                and x.qc_result.is_usable()
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
                    if distance > protocol.max_stored_distance:
                        continue
                    # Add to seq_distances
                    curr_seq_distances[i][seq_id2] = distance
                    curr_seq_distances[j][seq_id1] = distance

            # Create SeqDistance objects from distances
            for i, allele_profile in enumerate(curr_allele_profiles):
                # Calculate SeqDistance.id as 128 bit hash of sample_id, so that it is always the same
                seq_distance_id = UUID(
                    bytes=hashlib.sha256(allele_profile.sample_id.bytes).digest()[:16]
                )
                # Create seq_distance and add to dict_db
                seq_distance = model.SeqDistance(
                    id=seq_distance_id,
                    sample_id=allele_profile.sample_id,
                    protocol_id=protocol.id,
                    allele_profile_id=allele_profile.id,
                    distance_format=enum.SeqDistanceFormat.PROFILE_DISTANCE_MAP,
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

    def retrieve_similar_profiles(
        self,
        cmd: command.RetrieveSimilarProfilesCommand,
    ) -> list[UUID]:
        # Special case: zero query profile ids
        if not cmd.profile_ids:
            return []
        # Use dedicated repository method to retrieve similar profiles, which allows for more efficient retrieval of distances and distance formats
        with self.repository.uow() as uow:
            similar_profile_ids: list[UUID] = self.repository.retrieve_similar_profiles(
                uow,
                cmd.protocol_id,
                cmd.profile_ids,
                cmd.max_distance,
            )
        return similar_profile_ids

    def calculate_seq_distances_for_new_profiles(
        self,
        cmd: command.CalculateSeqDistancesForNewProfilesCommand,
    ) -> list[model.CalculateSeqDistancesResult]:
        return seq_service_calculate_seq_distances_for_new_profiles(self, cmd)

    def crud_protocol(
        self,
        cmd: command.ProtocolCrudCommand,
    ) -> (
        model.Protocol
        | list[model.Protocol]
        | UUID
        | list[UUID]
        | bool
        | list[bool]
        | None
    ):
        return seq_service_crud_protocol(self, cmd)

    def crud_allele(
        self,
        cmd: command.AlleleCrudCommand,
    ) -> (
        model.Allele | list[model.Allele] | UUID | list[UUID] | bool | list[bool] | None
    ):
        return seq_service_crud_allele(self, cmd)

    def crud_allele_profile(
        self,
        cmd: command.AlleleProfileCrudCommand,
    ) -> (
        model.AlleleProfile
        | list[model.AlleleProfile]
        | UUID
        | list[UUID]
        | bool
        | list[bool]
        | None
    ):
        return seq_service_crud_allele_profile(self, cmd)

    def crud_allele_profile_identifier(
        self,
        cmd: command.AlleleProfileIdentifierCrudCommand,
    ) -> (
        model.AlleleProfileIdentifier
        | list[model.AlleleProfileIdentifier]
        | UUID
        | list[UUID]
        | bool
        | list[bool]
        | None
    ):
        return seq_service_crud_allele_profile_identifier(self, cmd)

    def crud_ast_measurement(
        self,
        cmd: command.AstMeasurementCrudCommand,
    ) -> (
        model.AstMeasurement
        | list[model.AstMeasurement]
        | UUID
        | list[UUID]
        | bool
        | list[bool]
        | None
    ):
        return seq_service_crud_ast_measurement(self, cmd)

    def crud_ast_prediction(
        self,
        cmd: command.AstPredictionCrudCommand,
    ) -> (
        model.AstPrediction
        | list[model.AstPrediction]
        | UUID
        | list[UUID]
        | bool
        | list[bool]
        | None
    ):
        return seq_service_crud_ast_prediction(self, cmd)

    def crud_file(
        self,
        cmd: command.FileCrudCommand,
    ) -> model.File | list[model.File] | UUID | list[UUID] | bool | list[bool] | None:
        return seq_service_crud_file(self, cmd)

    def crud_kmer_profile(
        self,
        cmd: command.KmerProfileCrudCommand,
    ) -> (
        model.KmerProfile
        | list[model.KmerProfile]
        | UUID
        | list[UUID]
        | bool
        | list[bool]
        | None
    ):
        return seq_service_crud_kmer_profile(self, cmd)

    def crud_kmer_profile_identifier(
        self,
        cmd: command.KmerProfileIdentifierCrudCommand,
    ) -> (
        model.KmerProfileIdentifier
        | list[model.KmerProfileIdentifier]
        | UUID
        | list[UUID]
        | bool
        | list[bool]
        | None
    ):
        return seq_service_crud_kmer_profile_identifier(self, cmd)

    def crud_locus(
        self,
        cmd: command.LocusCrudCommand,
    ) -> model.Locus | list[model.Locus] | UUID | list[UUID] | bool | list[bool] | None:
        return seq_service_crud_locus(self, cmd)

    def crud_locus_code_map(
        self,
        cmd: command.LocusCodeMapCrudCommand,
    ) -> (
        model.LocusCodeMap
        | list[model.LocusCodeMap]
        | UUID
        | list[UUID]
        | bool
        | list[bool]
        | None
    ):
        return seq_service_crud_locus_code_map(self, cmd)

    def crud_locus_profile(
        self,
        cmd: command.LocusProfileCrudCommand,
    ) -> (
        model.LocusProfile
        | list[model.LocusProfile]
        | UUID
        | list[UUID]
        | bool
        | list[bool]
        | None
    ):
        return seq_service_crud_locus_profile(self, cmd)

    def crud_locus_profile_identifier(
        self,
        cmd: command.LocusProfileIdentifierCrudCommand,
    ) -> (
        model.LocusProfileIdentifier
        | list[model.LocusProfileIdentifier]
        | UUID
        | list[UUID]
        | bool
        | list[bool]
        | None
    ):
        return seq_service_crud_locus_profile_identifier(self, cmd)

    def crud_locus_set(
        self,
        cmd: command.LocusSetCrudCommand,
    ) -> (
        model.LocusSet
        | list[model.LocusSet]
        | UUID
        | list[UUID]
        | bool
        | list[bool]
        | None
    ):
        return seq_service_crud_locus_set(self, cmd)

    def crud_mlva_profile(
        self,
        cmd: command.MlvaProfileCrudCommand,
    ) -> (
        model.MlvaProfile
        | list[model.MlvaProfile]
        | UUID
        | list[UUID]
        | bool
        | list[bool]
        | None
    ):
        return seq_service_crud_mlva_profile(self, cmd)

    def crud_mlva_profile_identifier(
        self,
        cmd: command.MlvaProfileIdentifierCrudCommand,
    ) -> (
        model.MlvaProfileIdentifier
        | list[model.MlvaProfileIdentifier]
        | UUID
        | list[UUID]
        | bool
        | list[bool]
        | None
    ):
        return seq_service_crud_mlva_profile_identifier(self, cmd)

    def crud_pcr_measurement(
        self,
        cmd: command.PcrMeasurementCrudCommand,
    ) -> (
        model.PcrMeasurement
        | list[model.PcrMeasurement]
        | UUID
        | list[UUID]
        | bool
        | list[bool]
        | None
    ):
        return seq_service_crud_pcr_measurement(self, cmd)

    def crud_read_set(
        self,
        cmd: command.ReadSetCrudCommand,
    ) -> (
        model.ReadSet
        | list[model.ReadSet]
        | UUID
        | list[UUID]
        | bool
        | list[bool]
        | None
    ):
        return seq_service_crud_read_set(self, cmd)

    def crud_read_set_identifier(
        self,
        cmd: command.ReadSetIdentifierCrudCommand,
    ) -> (
        model.ReadSetIdentifier
        | list[model.ReadSetIdentifier]
        | UUID
        | list[UUID]
        | bool
        | list[bool]
        | None
    ):
        return seq_service_crud_read_set_identifier(self, cmd)

    def crud_ref_allele(
        self,
        cmd: command.RefAlleleCrudCommand,
    ) -> (
        model.RefAllele
        | list[model.RefAllele]
        | UUID
        | list[UUID]
        | bool
        | list[bool]
        | None
    ):
        return seq_service_crud_ref_allele(self, cmd)

    def crud_ref_seq(
        self,
        cmd: command.RefSeqCrudCommand,
    ) -> (
        model.RefSeq | list[model.RefSeq] | UUID | list[UUID] | bool | list[bool] | None
    ):
        return seq_service_crud_ref_seq(self, cmd)

    def crud_sample(
        self,
        cmd: command.SampleCrudCommand,
    ) -> (
        model.Sample | list[model.Sample] | UUID | list[UUID] | bool | list[bool] | None
    ):
        return seq_service_crud_sample(self, cmd)

    def crud_sample_data_collection_link(
        self,
        cmd: command.SampleDataCollectionLinkCrudCommand,
    ) -> (
        model.SampleDataCollectionLink
        | list[model.SampleDataCollectionLink]
        | UUID
        | list[UUID]
        | bool
        | list[bool]
        | None
    ):
        return seq_service_crud_sample_data_collection_link(self, cmd)

    def crud_sample_identifier(
        self,
        cmd: command.SampleIdentifierCrudCommand,
    ) -> (
        model.SampleIdentifier
        | list[model.SampleIdentifier]
        | UUID
        | list[UUID]
        | bool
        | list[bool]
        | None
    ):
        return seq_service_crud_sample_identifier(self, cmd)

    def crud_seq(
        self,
        cmd: command.SeqCrudCommand,
    ) -> model.Seq | list[model.Seq] | UUID | list[UUID] | bool | list[bool] | None:
        return seq_service_crud_seq(self, cmd)

    def crud_seq_category(
        self,
        cmd: command.SeqCategoryCrudCommand,
    ) -> (
        model.SeqCategory
        | list[model.SeqCategory]
        | UUID
        | list[UUID]
        | bool
        | list[bool]
        | None
    ):
        return seq_service_crud_seq_category(self, cmd)

    def crud_seq_category_set(
        self,
        cmd: command.SeqCategorySetCrudCommand,
    ) -> (
        model.SeqCategorySet
        | list[model.SeqCategorySet]
        | UUID
        | list[UUID]
        | bool
        | list[bool]
        | None
    ):
        return seq_service_crud_seq_category_set(self, cmd)

    def crud_seq_classification(
        self,
        cmd: command.SeqClassificationCrudCommand,
    ) -> (
        model.SeqClassification
        | list[model.SeqClassification]
        | UUID
        | list[UUID]
        | bool
        | list[bool]
        | None
    ):
        return seq_service_crud_seq_classification(self, cmd)

    def crud_seq_distance(
        self,
        cmd: command.SeqDistanceCrudCommand,
    ) -> (
        model.SeqDistance
        | list[model.SeqDistance]
        | UUID
        | list[UUID]
        | bool
        | list[bool]
        | None
    ):
        return seq_service_crud_seq_distance(self, cmd)

    def crud_seq_identifier(
        self,
        cmd: command.SeqIdentifierCrudCommand,
    ) -> (
        model.SeqIdentifier
        | list[model.SeqIdentifier]
        | UUID
        | list[UUID]
        | bool
        | list[bool]
        | None
    ):
        return seq_service_crud_seq_identifier(self, cmd)

    def crud_seq_taxonomy(
        self,
        cmd: command.SeqTaxonomyCrudCommand,
    ) -> (
        model.SeqTaxonomy
        | list[model.SeqTaxonomy]
        | UUID
        | list[UUID]
        | bool
        | list[bool]
        | None
    ):
        return seq_service_crud_seq_taxonomy(self, cmd)

    def crud_snp_profile(
        self,
        cmd: command.SnpProfileCrudCommand,
    ) -> (
        model.SnpProfile
        | list[model.SnpProfile]
        | UUID
        | list[UUID]
        | bool
        | list[bool]
        | None
    ):
        return seq_service_crud_snp_profile(self, cmd)

    def crud_snp_profile_identifier(
        self,
        cmd: command.SnpProfileIdentifierCrudCommand,
    ) -> (
        model.SnpProfileIdentifier
        | list[model.SnpProfileIdentifier]
        | UUID
        | list[UUID]
        | bool
        | list[bool]
        | None
    ):
        return seq_service_crud_snp_profile_identifier(self, cmd)

    def crud_taxon(
        self,
        cmd: command.TaxonCrudCommand,
    ) -> model.Taxon | list[model.Taxon] | UUID | list[UUID] | bool | list[bool] | None:
        return seq_service_crud_taxon(self, cmd)

    def crud_taxon_set(
        self,
        cmd: command.TaxonSetCrudCommand,
    ) -> (
        model.TaxonSet
        | list[model.TaxonSet]
        | UUID
        | list[UUID]
        | bool
        | list[bool]
        | None
    ):
        return seq_service_crud_taxon_set(self, cmd)

    def crud_taxon_set_member(
        self,
        cmd: command.TaxonSetMemberCrudCommand,
    ) -> (
        model.TaxonSetMember
        | list[model.TaxonSetMember]
        | UUID
        | list[UUID]
        | bool
        | list[bool]
        | None
    ):
        return seq_service_crud_taxon_set_member(self, cmd)

    def crud_tree_algorithm(
        self,
        cmd: command.TreeAlgorithmCrudCommand,
    ) -> (
        model.TreeAlgorithm
        | list[model.TreeAlgorithm]
        | UUID
        | list[UUID]
        | bool
        | list[bool]
        | None
    ):
        return seq_service_crud_tree_algorithm(self, cmd)

    def crud_tree_algorithm_class(
        self,
        cmd: command.TreeAlgorithmClassCrudCommand,
    ) -> (
        model.TreeAlgorithmClass
        | list[model.TreeAlgorithmClass]
        | UUID
        | list[UUID]
        | bool
        | list[bool]
        | None
    ):
        return seq_service_crud_tree_algorithm_class(self, cmd)
