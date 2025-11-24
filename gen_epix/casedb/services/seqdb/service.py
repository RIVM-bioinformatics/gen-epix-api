import importlib
from collections.abc import Hashable, Iterable
from typing import Any
from uuid import UUID

from gen_epix.casedb.domain import command
from gen_epix.casedb.domain import enum as enum
from gen_epix.casedb.domain import exc, model
from gen_epix.casedb.domain.service import BaseSeqdbService
from gen_epix.commondb.config import AppCfg
from gen_epix.commondb.domain.enum import AppType
from gen_epix.fastapp import App, CrudCommand, Model
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.seqdb.domain import command as seqdb_command
from gen_epix.seqdb.domain import enum as seqdb_enum
from gen_epix.seqdb.domain import model as seqdb_model
from gen_epix.seqdb.domain.model import User as SeqdbUser
from gen_epix.seqdb.env import AppComposer as SeqdbAppComposer


class SeqdbService(BaseSeqdbService):

    COMMAND_MAP: dict[type[command.Command], type[seqdb_command.Command]] = {
        command.RetrievePhylogeneticTreeBySequencesCommand: seqdb_command.RetrievePhylogeneticTreeCommand,
    }
    TREE_ALGORITHM_MAP = {
        x: y
        for x in enum.TreeAlgorithmType
        for y in seqdb_enum.TreeAlgorithm
        if x.value == y.value
    }

    def __init__(self, app: App, seqdb_app_type: str, **kwargs: Any) -> None:
        seqdb_local_app_props = kwargs.pop("seqdb_local_app", {})
        seqdb_remote_app_props = kwargs.pop("seqdb_remote_app", {})
        super().__init__(app, **kwargs)
        seqdb_app: App
        seqdb_user: SeqdbUser | None
        if seqdb_app_type.upper() == "LOCAL":
            if "app_cfg" in seqdb_local_app_props:
                seqdb_app_cfg = seqdb_local_app_props.pop("app_cfg")
            else:
                seqdb_app_cfg = AppCfg(
                    AppType.SEQDB, seqdb_enum.ServiceType, seqdb_enum.RepositoryType
                )
            log_setup = seqdb_local_app_props.get(
                "log_setup", kwargs.get("logger") is not None
            )
            seqdb_app_composer = SeqdbAppComposer(seqdb_app_cfg, log_setup=log_setup)
            seqdb_app = seqdb_app_composer.app
            seqdb_user = SeqdbUser(**seqdb_local_app_props["user"])
        elif seqdb_app_type.upper() == "REMOTE":
            remote_app_module = seqdb_remote_app_props.pop("module")
            remote_app_class_name = seqdb_remote_app_props.pop("class_name")
            remote_app_class = getattr(
                importlib.import_module(remote_app_module), remote_app_class_name
            )
            seqdb_app = remote_app_class(**seqdb_remote_app_props)
            seqdb_user = None
        else:
            raise exc.InitializationServiceError(
                f"Invalid seqdb_app_type: {seqdb_app_type}. Must be 'LOCAL' or 'REMOTE'."
            )
        self._seqdb_app = seqdb_app
        self._seqdb_user = seqdb_user

    @property
    def seqdb_app(self) -> App:
        return self._seqdb_app

    @property
    def seqdb_user(self) -> SeqdbUser | None:
        return self._seqdb_user

    def retrieve_phylogenetic_tree(
        self, cmd: command.RetrievePhylogeneticTreeBySequencesCommand
    ) -> model.PhylogeneticTree | None:
        user = cmd.user
        # Prepare seqdb command and calculate tree via seqdb
        leaf_id_mapper = cmd.props.get("leaf_id_mapper")
        if leaf_id_mapper:
            leaf_names = [str(leaf_id_mapper(x)) for x in cmd.sequence_ids]
        else:
            leaf_names = None
        seqdb_cmd = seqdb_command.RetrievePhylogeneticTreeCommand(
            user=self.seqdb_user,
            seq_distance_protocol_id=cmd.seqdb_seq_distance_protocol_id,
            tree_algorithm=seqdb_enum.TreeAlgorithm[cmd.tree_algorithm_code.value],
            seq_ids=cmd.sequence_ids,
            leaf_names=leaf_names,
        )
        seqdb_phylogenetic_tree: seqdb_model.PhylogeneticTree = self.seqdb_app.handle(
            seqdb_cmd
        )
        # Convert seqdb tree model to casedb model
        phylogenetic_tree = model.PhylogeneticTree(
            tree_algorithm_code=cmd.tree_algorithm_code,
            sequence_ids=seqdb_phylogenetic_tree.seq_ids,
            leaf_ids=(
                [UUID(x) for x in seqdb_phylogenetic_tree.leaf_names]
                if seqdb_phylogenetic_tree.leaf_names is not None
                else None
            ),
            newick_repr=seqdb_phylogenetic_tree.newick_repr,
        )
        return phylogenetic_tree

    def _retrieve_seq_objects_by_ids(
        self, seq_ids: list[UUID]
    ) -> list[seqdb_model.Seq]:
        seqs: list[seqdb_model.Seq] = self.seqdb_app.handle(
            seqdb_command.SeqCrudCommand(
                user=self.seqdb_user,
                obj_ids=seq_ids,
                operation=CrudOperation.READ_SOME,
            )
        )
        return seqs

    def retrieve_genetic_sequences(
        self, cmd: command.RetrieveGeneticSequenceByIdCommand
    ) -> list[model.GeneticSequence]:
        # naive implementation that retrieves sequences by ID
        seqs: list[seqdb_model.Seq] = self._retrieve_seq_objects_by_ids(cmd.seq_ids)
        file_ids = [seq.file_id for seq in seqs if seq.file_id is not None]
        files: list[seqdb_model.File] = self._seqdb_app.handle(
            seqdb_command.FileCrudCommand(
                user=cmd.user,
                obj_ids=list(set(file_ids)),  # type: ignore[arg-type]
                operation=CrudOperation.READ_SOME,
            )
        )
        file_map = {x.id: x for x in files}
        # Convert raw sequences to model.GeneticSequence
        genetic_sequences = [
            # TODO: handle parsing a single raw sequence from the file
            model.GeneticSequence(
                id=seq.id,
                nucleotide_sequence=file_map[file_id].content.decode(encoding="utf-8"),
                distances={},
            )
            for seq, file_id in zip(seqs, file_ids)
        ]
        return genetic_sequences

    def retrieve_genetic_sequence_fasta_by_id(
        self,
        cmd: command.RetrieveGeneticSequenceFastaByIdCommand,
    ) -> Iterable[str]:
        seqdb_cmd = seqdb_command.RetrieveSeqFastaCommand(
            user=self.seqdb_user,
            seq_ids=cmd.seq_ids,
            wrap=cmd.wrap,
        )
        fasta_iterator: Iterable[str] = self.seqdb_app.handle(seqdb_cmd)
        return fasta_iterator

    def crud(
        self, cmd: CrudCommand
    ) -> Hashable | list[Hashable] | Model | list[Model] | bool | list[bool] | None:
        """
        Generic CRUD operation handler that forwards the command to seqdb while
        setting the functional user.
        """
        casedb_user = cmd.user
        cmd.user = self.seqdb_user
        result = self.seqdb_app.handle(cmd)
        cmd.user = casedb_user
        return result  # type: ignore[no-any-return]
