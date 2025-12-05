import gzip
import hashlib
import logging
import uuid
from enum import Enum
from pathlib import Path
from test.seqdb.seqdb_endpoint_test_client import SeqdbEndpointTestClient
from test.test_client.util import get_test_name, get_test_output_dir
from typing import Any
from uuid import UUID

from gen_epix.commondb.api.exc import LAST_HANDLED_EXCEPTION
from gen_epix.commondb.app_setup import create_fast_api
from gen_epix.commondb.config import AppCfg, BaseAppCfg
from gen_epix.commondb.test.test_client import TestClient
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.seqdb.api.router import create_routers
from gen_epix.seqdb.domain import command, enum, model
from gen_epix.seqdb.env import AppComposer


class SeqdbTestClient(TestClient):
    TEST_CLIENTS: dict[str, "SeqdbTestClient"] = {}

    MODEL_KEY_MAP = TestClient.MODEL_KEY_MAP | {
        model.User: "name",
        model.UserInvitation: "email",
        model.OrganizationAdminPolicy: ("organization_id", "user_id"),
        model.DataCollection: "name",
        model.PcrProtocol: "name",
        model.AstProtocol: "name",
        model.SequencingProtocol: "name",
        model.AssemblyProtocol: "name",
        model.AlignmentProtocol: "name",
        model.TaxonomyProtocol: "name",
        model.SeqClassificationProtocol: "name",
        model.SeqDistanceProtocol: "name",
        model.LocusDetectionProtocol: "name",
        model.SnpDetectionProtocol: "name",
        model.MlvaDetectionProtocol: "name",
        model.KmerDetectionProtocol: "name",
        model.Sample: "code",
        model.File: "id",
        model.ReadSet: "id",
        model.Seq: "id",
    }

    DUMMY_VALUES: dict[str, Any] = {
        "fwd_reads_uri1": "http://reads/sample_x_1.fastq",
        "rev_reads_uri1": "http://reads/sample_x_2.fastq",
        "fwd_fastq_content1": ["@read1", "A" * 100, "+", "I" * 100],
        "rev_fastq_content1": ["@read1", "T" * 100, "+", "I" * 100],
        "fasta_content1": [
            ">contig1",
            "A" * 80,
            "C" * 80,
            ">contig2",
            "G" * 80,
            "T" * 80,
        ],
        "invalid_fastq_bytes1": b"INVALID_FASTQ_CONTENT",
        "invalid_fasta_bytes1": b"INVALID_FASTA_CONTENT",
    }
    DUMMY_VALUES["fwd_fastq_bytes1"] = "\n".join(
        DUMMY_VALUES["fwd_fastq_content1"]
    ).encode()
    DUMMY_VALUES["rev_fastq_bytes1"] = "\n".join(
        DUMMY_VALUES["rev_fastq_content1"]
    ).encode()
    DUMMY_VALUES["fwd_fastq_gzip_bytes1"] = gzip.compress(
        DUMMY_VALUES["fwd_fastq_bytes1"]
    )
    DUMMY_VALUES["rev_fastq_gzip_bytes1"] = gzip.compress(
        DUMMY_VALUES["rev_fastq_bytes1"]
    )
    DUMMY_VALUES["fasta_bytes1"] = "\n".join(DUMMY_VALUES["fasta_content1"]).encode()
    DUMMY_VALUES["fasta_gzip_bytes1"] = gzip.compress(DUMMY_VALUES["fasta_bytes1"])
    DUMMY_VALUES["fwd_reads_hash1"] = UUID(
        hashlib.sha256(DUMMY_VALUES["fwd_fastq_bytes1"]).digest()[0:16].hex()
    )
    DUMMY_VALUES["rev_reads_hash1"] = UUID(
        hashlib.sha256(DUMMY_VALUES["rev_fastq_bytes1"]).digest()[0:16].hex()
    )
    DUMMY_VALUES["fasta_file_hash1"] = UUID(
        hashlib.sha256(DUMMY_VALUES["fasta_bytes1"]).digest()[0:16].hex()
    )

    @classmethod
    def get_test_client(
        cls,
        test_type: str,
        app_cfg: AppCfg,
        verbose: bool = False,
        log_level: int = logging.ERROR,
        log_setup: bool = False,
        **kwargs: Any,
    ) -> "TestClient":
        """
        Create a test environment for the given test type and repository type. A
        single environment, with a common test directory, is kept for each test type.
        """
        if app_cfg.name not in cls.TEST_CLIENTS:
            test_name = get_test_name(test_type)
            test_dir = get_test_output_dir(test_name)
            is_new_test_dir = True
            # Find existing test dir for same test type and use that if found,
            # so all results come in the same dir
            for stored_name, stored_env in cls.TEST_CLIENTS.items():
                if stored_name.startswith(test_type):
                    test_name = stored_env.test_name
                    test_dir = stored_env.test_dir
                    is_new_test_dir = False
                    break
            # Adjust config to new dir and copy any repository files there
            if is_new_test_dir:
                app_cfg.copy_repository_files(test_dir)
            cls.TEST_CLIENTS[app_cfg.name] = cls(
                test_name,
                test_dir,
                app_cfg,
                verbose=verbose,
                log_level=log_level,
                log_setup=log_setup,
                **kwargs,
            )
        return cls.TEST_CLIENTS[app_cfg.name]  # type: ignore[no-any-return]

    def __init__(
        self,
        test_name: str,
        test_dir: Path,
        app_cfg: BaseAppCfg,
        verbose: bool = False,
        log_level: int = logging.ERROR,
        log_setup: bool = False,
        use_endpoints: bool = False,
        default_route_prefix: str | None = None,
        **kwargs: Any,
    ):
        # Set and adjust cfg
        app_cfg.cfg["app"]["debug"] = True
        curr_cfg = app_cfg.cfg["service"]["auth"]["props"]["root"]
        curr_cfg["organization"]["name"] = "org1"
        curr_cfg["user"]["key"] = "root1_1@org1.org"
        curr_cfg["user"]["email"] = "root1_1@org1.org"
        curr_cfg["user"]["name"] = "root1_1"

        # Create app
        TestClient._set_log_level(app_cfg, log_level)
        app_composer = AppComposer(app_cfg, log_setup=log_setup, **kwargs)

        # Create endpoint test client if endpoints are to be used (including own
        # app_composer), otherwise construct app env separately
        endpoint_test_client: SeqdbEndpointTestClient | None = None
        app_last_handled_exception: dict | None = None
        if use_endpoints:
            fast_api = create_fast_api(
                app=app_composer.app,
                create_routers_fn=create_routers,
                setup_logger=app_cfg.setup_logger if log_setup else None,
                api_logger=app_cfg.api_logger,
                debug=True,
                update_openapi_schema=True,
            )
            app_last_handled_exception = LAST_HANDLED_EXCEPTION
            endpoint_test_client = SeqdbEndpointTestClient(
                app_composer.app,
                fast_api,
                app_last_handled_exception,
                **kwargs,
            )

        # Call base class constructor
        super().__init__(
            test_name,
            test_dir,
            app_cfg,
            app_composer,
            verbose=verbose,
            log_level=log_level,
            use_endpoints=use_endpoints,
            endpoint_test_client=endpoint_test_client,
            app_last_handled_exception=app_last_handled_exception,
            **kwargs,
        )

    def create_sequencing_protocol(
        self,
        user_or_str: str | model.User,
        code: str,
        name: str | None = None,
    ) -> model.SequencingProtocol:
        return self._create_protocol(
            model.SequencingProtocol,
            user_or_str,
            code,
            name,
        )  # type:ignore[return-value]

    def create_assembly_protocol(
        self,
        user_or_str: str | model.User,
        code: str,
        name: str | None = None,
        has_manual_curation: bool = False,
    ) -> model.AssemblyProtocol:
        return self._create_protocol(
            model.AssemblyProtocol,
            user_or_str,
            code,
            name,
            has_manual_curation=has_manual_curation,
        )  # type:ignore[return-value]

    def create_locus_detection_protocol(
        self,
        user_or_str: str | model.User,
        code: str,
        name: str | None = None,
    ) -> model.LocusDetectionProtocol:
        return self._create_protocol(
            model.LocusDetectionProtocol,
            user_or_str,
            code,
            name,
        )  # type:ignore[return-value]

    def create_pcr_protocol(
        self,
        user_or_str: str | model.User,
        code: str,
        name: str | None = None,
        target_names: list[str] = ["gene1", "gene2"],
    ) -> model.PcrProtocol:
        return self._create_protocol(
            model.PcrProtocol,
            user_or_str,
            code,
            name,
            target_names=target_names,  # Required field
        )  # type:ignore[return-value]

    def create_ast_protocol(
        self,
        user_or_str: str | model.User,
        code: str,
        name: str | None = None,
        is_predicted: bool = False,
        antimicrobial_names: list[str] = ["amoxicillin", "tetracycline"],
    ) -> model.AstProtocol:
        return self._create_protocol(
            model.AstProtocol,
            user_or_str,
            code,
            name,
            is_predicted=is_predicted,  # Required field
            antimicrobial_names=antimicrobial_names,  # Required field
        )  # type:ignore[return-value]

    def create_alignment_protocol(
        self,
        user_or_str: str | model.User,
        code: str,
        name: str | None = None,
        is_multiple: bool = False,
    ) -> model.AlignmentProtocol:
        return self._create_protocol(
            model.AlignmentProtocol,
            user_or_str,
            code,
            name,
            is_multiple=is_multiple,  # Required field
        )  # type:ignore[return-value]

    def create_taxonomy_protocol(
        self,
        user_or_str: str | model.User,
        code: str,
        name: str | None = None,
    ) -> model.TaxonomyProtocol:
        return self._create_protocol(
            model.TaxonomyProtocol,
            user_or_str,
            code,
            name,
        )  # type:ignore[return-value]

    def create_seq_classification_protocol(
        self,
        user_or_str: str | model.User,
        code: str,
        name: str | None = None,
        is_taxonomic: bool = True,
    ) -> model.SeqClassificationProtocol:
        return self._create_protocol(
            model.SeqClassificationProtocol,
            user_or_str,
            code,
            name,
            is_taxonomic=is_taxonomic,  # Required field
        )  # type:ignore[return-value]

    def create_seq_distance_protocol(
        self,
        user_or_str: str | model.User,
        code: str,
        name: str | None = None,
        is_integer_distance: bool = True,
        seq_distance_protocol_type: enum.SeqDistanceProtocolType = enum.SeqDistanceProtocolType.OTHER,
        max_stored_distance: float = 100.0,
    ) -> model.SeqDistanceProtocol:
        return self._create_protocol(
            model.SeqDistanceProtocol,
            user_or_str,
            code,
            name,
            is_integer_distance=is_integer_distance,  # Required field
            seq_distance_protocol_type=seq_distance_protocol_type,  # Required field - using OTHER to avoid locus_set_id requirement
            max_stored_distance=max_stored_distance,  # Required field
        )  # type:ignore[return-value]

    def create_snp_detection_protocol(
        self,
        user_or_str: str | model.User,
        code: str,
        name: str | None = None,
    ) -> model.SnpDetectionProtocol:
        return self._create_protocol(
            model.SnpDetectionProtocol,
            user_or_str,
            code,
            name,
        )  # type:ignore[return-value]

    def create_mlva_detection_protocol(
        self,
        user_or_str: str | model.User,
        code: str,
        name: str | None = None,
    ) -> model.MlvaDetectionProtocol:
        return self._create_protocol(
            model.MlvaDetectionProtocol,
            user_or_str,
            code,
            name,
        )  # type:ignore[return-value]

    def create_kmer_detection_protocol(
        self,
        user_or_str: str | model.User,
        code: str,
        name: str | None = None,
    ) -> model.KmerDetectionProtocol:
        return self._create_protocol(
            model.KmerDetectionProtocol,
            user_or_str,
            code,
            name,
        )  # type:ignore[return-value]

    def create_sample(
        self,
        user_or_str: str | model.User,
        created_in_data_collection_or_str: str | model.DataCollection | None = None,
        code: str | None = None,
        props: dict[str, str | int | float | None] | None = None,
        set_dummy_created_in_data_collection: bool = False,
    ) -> model.Sample:
        user: model.User = self._get_obj(
            self.user_class, user_or_str
        )  # type:ignore[assignment]
        created_in_data_collection_id = self._get_obj_id(
            model.DataCollection,
            created_in_data_collection_or_str,
            set_dummy_created_in_data_collection,
        )
        sample: model.Sample = self.app.handle(
            command.SampleCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.Sample(  # type: ignore[arg-type]
                    code=code,
                    props=props,
                    created_in_data_collection_id=created_in_data_collection_id,
                ),
            )
        )
        return self._set_obj(sample)

    def create_file(
        self,
        user_or_str: str | model.User,
        content_or_str: bytes | str | list[str],
        format: enum.FileFormat,
        compression: enum.FileCompression = enum.FileCompression.NONE,
    ) -> model.File:
        user: model.User = self._get_obj(
            self.user_class, user_or_str
        )  # type:ignore[assignment]
        content: bytes
        if isinstance(content_or_str, str):
            content = content_or_str.encode()
        elif isinstance(content_or_str, list):
            content = "\n".join(content_or_str).encode()
        else:
            content = content_or_str
        file_id: UUID = self.app.handle(
            command.CreateFileCommand(
                user=user,
                file=model.File(content=content),
                format=format,
                compression=compression,
            )
        )

        return self._set_obj(
            model.File(id=file_id, content=content)
        )  # type:ignore[return-value]

    def create_read_set(
        self,
        user_or_str: str | model.User,
        sample_or_str: str | model.Sample | None = None,
        sequencing_protocol_or_str: model.SequencingProtocol | str | None = None,
        fwd_uri: str | None = None,
        rev_uri: str | None = None,
        fwd_file_id: UUID | None = None,
        rev_file_id: UUID | None = None,
        file_format: enum.FileFormat | None = None,
        file_compression: enum.FileCompression | None = None,
        fwd_reads_hash: UUID | str | None = None,
        rev_reads_hash: UUID | str | None = None,
        sequencing_run_code: str | None = None,
        set_dummy_sample: bool = False,
        set_dummy_sequencing_protocol: bool = False,
    ) -> model.ReadSet:
        user: model.User = self._get_obj(
            self.user_class, user_or_str
        )  # type:ignore[assignment]
        sample_id = self._get_obj_id(model.Sample, sample_or_str, set_dummy_sample)
        sequencing_protocol_id = self._get_obj_id(
            model.SequencingProtocol,
            sequencing_protocol_or_str,
            set_dummy_sequencing_protocol,
        )
        if isinstance(file_format, Enum) and not isinstance(
            file_format, enum.ReadsFileFormat
        ):
            file_format = enum.ReadsFileFormat(file_format.value)
        fwd_reads_hash: UUID | None
        if isinstance(fwd_reads_hash, str):
            fwd_reads_hash = UUID(fwd_reads_hash)
        rev_reads_hash: UUID | None
        if isinstance(rev_reads_hash, str):
            rev_reads_hash = UUID(rev_reads_hash)
        read_set: model.ReadSet = self.app.handle(
            command.ReadSetCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.ReadSet(
                    sample_id=sample_id,
                    sequencing_protocol_id=sequencing_protocol_id,
                    fwd_uri=fwd_uri,
                    rev_uri=rev_uri,
                    fwd_file_id=fwd_file_id,
                    rev_file_id=rev_file_id,
                    file_format=file_format,
                    file_compression=file_compression,
                    fwd_reads_hash=fwd_reads_hash,
                    rev_reads_hash=rev_reads_hash,
                    sequencing_run_code=sequencing_run_code,
                ),
            )
        )
        assert read_set.sample_id == sample_id
        assert read_set.sequencing_protocol_id == sequencing_protocol_id
        assert read_set.fwd_reads_hash == fwd_reads_hash
        assert read_set.rev_reads_hash == rev_reads_hash
        assert read_set.fwd_file_id == fwd_file_id
        assert read_set.rev_file_id == rev_file_id
        assert read_set.fwd_uri == fwd_uri
        assert read_set.rev_uri == rev_uri
        return self._set_obj(read_set)

    def create_seq(
        self,
        user_or_str: str | model.User,
        sample_or_str: model.Sample | str | None = None,
        read_set_id: UUID | None = None,
        read_set2_id: UUID | None = None,
        assembly_protocol_or_str: model.AssemblyProtocol | str | None = None,
        file_id: UUID | None = None,
        file_format: enum.SeqFileFormat | None = None,
        file_compression: enum.FileCompression | None = None,
        set_dummy_sample: bool = False,
        set_dummy_assembly_protocol: bool = False,
    ) -> model.Seq:
        user: model.User = self._get_obj(
            self.user_class, user_or_str
        )  # type:ignore[assignment]
        sample_id = self._get_obj_id(model.Sample, sample_or_str, set_dummy_sample)
        assembly_protocol_id = self._get_obj_id(
            model.AssemblyProtocol,
            assembly_protocol_or_str,
            set_dummy_assembly_protocol,
        )
        if isinstance(file_format, Enum) and not isinstance(
            file_format, enum.SeqFileFormat
        ):
            file_format = enum.SeqFileFormat(file_format.value)
        seq: model.Seq = self.app.handle(
            command.SeqCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.Seq(
                    sample_id=sample_id,
                    read_set_id=read_set_id,
                    read_set2_id=read_set2_id,
                    assembly_protocol_id=assembly_protocol_id,
                    file_id=file_id,
                    file_format=file_format,
                    file_compression=file_compression,
                ),
            )
        )
        assert seq.assembly_protocol_id == assembly_protocol_id
        return self._set_obj(seq)  # type:ignore[return-value]

    def _create_protocol(
        self,
        protocol_class: type[model.Model],
        user_or_str: str | model.User,
        code: str,
        name: str | None = None,
        **kwargs: Any,
    ) -> model.Model:
        user: model.User = self._get_obj(
            self.user_class, user_or_str
        )  # type:ignore[assignment]
        user: model.User = self._get_obj(
            self.user_class, user_or_str
        )  # type:ignore[assignment]
        crud_command_class = self.app.domain.get_crud_command_for_model(protocol_class)
        protocol = self.app.handle(
            crud_command_class(
                operation=CrudOperation.CREATE_ONE,
                user=user,
                objs=protocol_class(
                    code=code, name=name if name else code, **kwargs
                ),  # type:ignore
            )
        )
        return self._set_obj(protocol)  # type:ignore[return-value]

    def _get_obj_id(
        self,
        model_class: type[model.Model],
        obj_or_str: str | model.Model | None,
        create_dummy_id: bool,
    ) -> UUID:
        obj_id: UUID
        if create_dummy_id:
            if obj_or_str is not None:
                raise ValueError("obj_or_str must be None when create_dummy_id is True")
            obj_id = uuid.uuid4()
        else:
            if obj_or_str is None:
                raise ValueError(
                    "obj_or_str must be provided when create_dummy_id is False"
                )
            obj_id = (  # type:ignore[union-attr]
                self._get_obj(  # type:ignore[assignment]
                    model_class, obj_or_str
                )
            ).id  # type:ignore[assignment]
        return obj_id
