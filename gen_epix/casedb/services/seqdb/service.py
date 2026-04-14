from collections.abc import Hashable, Iterable
from typing import Any
from uuid import UUID

from gen_epix.casedb.domain import command, enum, model
from gen_epix.casedb.domain.service import BaseSeqdbService
from gen_epix.commondb.domain.enum import AppType
from gen_epix.commondb.services import CommondbRemoteApp
from gen_epix.fastapp import App, Model
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.seqdb.domain import command as seqdb_command
from gen_epix.seqdb.domain import enum as seqdb_enum
from gen_epix.seqdb.domain import model as seqdb_model
from gen_epix.seqdb.domain.model import User as SeqdbUser
from gen_epix.seqdb.env import AppComposer as SeqdbAppComposer


class SeqdbService(BaseSeqdbService):

    COMMAND_MAP: dict[type[command.Command], type[command.Command]] = {
        command.RetrievePhylogeneticTreeByProfilesCommand: seqdb_command.CalculatePhylogeneticTreeCommand,
        command.RetrieveSimilarCasesCommand: seqdb_command.RetrieveSimilarProfilesCommand,
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
        seqdb_app, seqdb_user = CommondbRemoteApp.create_local_or_remote_app(
            AppType.SEQDB,
            app_setup_type=seqdb_app_type,
            local_app_props=seqdb_local_app_props,
            remote_app_props=seqdb_remote_app_props,
            user_class=SeqdbUser,
            app_composer_class=SeqdbAppComposer,
            service_type_enum=seqdb_enum.ServiceType,
            repository_type_enum=seqdb_enum.RepositoryType,
            logger=kwargs.get("logger"),
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
        self, cmd: command.RetrievePhylogeneticTreeByProfilesCommand
    ) -> model.PhylogeneticTree | None:
        user = cmd.user
        # Prepare seqdb command and calculate tree via seqdb
        self.app.create_log_message(
            "8d761288",
            cmd.model_dump_json(),
        )
        leaf_id_mapper = cmd.props.get("leaf_id_mapper")
        if leaf_id_mapper:
            leaf_names = [str(leaf_id_mapper(x)) for x in cmd.profile_ids]
        else:
            leaf_names = None
        seqdb_cmd = seqdb_command.CalculatePhylogeneticTreeCommand(
            user=self.seqdb_user,
            protocol_id=cmd.seqdb_protocol_id,
            tree_algorithm=seqdb_enum.TreeAlgorithm[cmd.tree_algorithm_code.value],
            seq_profile_ids=cmd.profile_ids,
            leaf_names=leaf_names,
            allowed_qc_results=cmd.allowed_qc_results,
        )
        self.app.create_log_message(
            "ebb004e7",
            seqdb_cmd.model_dump_json(),
        )
        seqdb_phylogenetic_tree: seqdb_model.PhylogeneticTree = self.seqdb_app.handle(
            seqdb_cmd
        )
        # Convert seqdb tree model to casedb model
        phylogenetic_tree = model.PhylogeneticTree(
            tree_algorithm_code=cmd.tree_algorithm_code,
            profile_ids=seqdb_phylogenetic_tree.profile_ids,
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

    def upload_samples(
        self,
        cmd: seqdb_command.UploadSamplesCommand,
    ) -> seqdb_model.SampleBatchUploadResult:
        user = cmd.user
        cmd.user = self.seqdb_user
        result: seqdb_model.SampleBatchUploadResult = self.seqdb_app.handle(cmd)
        cmd.user = user
        return result

    def crud(
        self, cmd: command.CrudCommand
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

    def create_file(
        self,
        cmd: seqdb_command.CreateFileCommand,
    ) -> UUID:
        user = cmd.user
        cmd.user = self.seqdb_user
        file_id: UUID = self.seqdb_app.handle(cmd)
        cmd.user = user
        return file_id

    def retrieve_similar_profiles(
        self,
        cmd: seqdb_command.RetrieveSimilarProfilesCommand,
    ) -> list[UUID]:
        user = cmd.user
        cmd.user = self.seqdb_user
        similar_profile_ids: list[UUID] = self.seqdb_app.handle(cmd)
        cmd.user = user
        return similar_profile_ids
