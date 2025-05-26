from uuid import UUID

from gen_epix.casedb.domain import command, model
from gen_epix.casedb.domain.service.seqdb import BaseSeqdbService
from gen_epix.fastapp import App
from gen_epix.seqdb.domain.command import (
    RetrievePhylogeneticTreeCommand as SeqdbRetrievePhylogeneticTreeCommand,
)
from gen_epix.seqdb.domain.enum import Role as SeqdbRole
from gen_epix.seqdb.domain.enum import TreeAlgorithm as SeqdbTreeAlgorithm
from gen_epix.seqdb.domain.model import PhylogeneticTree as SeqdbPhylogeneticTree
from gen_epix.seqdb.domain.model import User as SeqdbUser


class SeqdbService(BaseSeqdbService):

    def __init__(self, app: App, ext_app: App, **kwargs: dict) -> None:
        super().__init__(app, **kwargs)
        self._ext_app = ext_app
        # TODO: get user from config data
        self._functional_user = SeqdbUser(
            id=UUID("00000000-0000-0000-0000-000000000001"),
            email="functional.user@org.org",
            roles={SeqdbRole.ADMIN},
            data_collection_ids=set(),
        )

    @property
    def ext_app(self) -> App:
        return self._ext_app

    @property
    def functional_user(self) -> SeqdbUser:
        return self._functional_user

    def retrieve_phylogenetic_tree(
        self, cmd: command.RetrievePhylogeneticTreeBySequencesCommand
    ) -> model.PhylogeneticTree | None:
        user = cmd.user
        leaf_id_mapper = cmd.props.get("leaf_id_mapper")
        if leaf_id_mapper:
            leaf_names = [str(leaf_id_mapper(x)) for x in cmd.sequence_ids]
        else:
            leaf_names = None
        seqdb_cmd = SeqdbRetrievePhylogeneticTreeCommand(
            user=self.functional_user,
            seq_distance_protocol_id=cmd.seqdb_seq_distance_protocol_id,
            tree_algorithm=SeqdbTreeAlgorithm[cmd.tree_algorithm_code.value],
            seq_ids=cmd.sequence_ids,
            leaf_names=leaf_names,
        )
        seqdb_phylogenetic_tree: SeqdbPhylogeneticTree = self.ext_app.handle(seqdb_cmd)
        phylogenetic_tree = model.PhylogeneticTree(
            tree_algorithm_code=cmd.tree_algorithm_code,
            sequence_ids=seqdb_phylogenetic_tree.seq_ids,
            leaf_ids=(
                [UUID(x) for x in seqdb_phylogenetic_tree.leaf_names]
                if seqdb_phylogenetic_tree.leaf_names
                else None
            ),
            newick_repr=seqdb_phylogenetic_tree.newick_repr,
        )
        return phylogenetic_tree

    def retrieve_genetic_sequences(self, cmd) -> list[model.GeneticSequence]:
        raise NotImplementedError()

    # def retrieve_allele_profile(
    #     self,
    #     cmd: command.RetrieveAlleleProfileCommand,
    # ) -> model.SeqDbAlleleProfile:
    #     raise NotImplementedError()
