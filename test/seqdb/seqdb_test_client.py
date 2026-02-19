import gzip
import hashlib
import logging
import random
import uuid
from enum import Enum
from functools import cached_property
from pathlib import Path
from test.seqdb.seqdb_endpoint_test_client import SeqdbEndpointTestClient
from test.test_client.util import get_test_name, get_test_output_dir
from typing import Any, Optional
from uuid import UUID

import numpy as np
from pydantic import BaseModel, computed_field, field_validator
from scipy.sparse import dok_matrix

from gen_epix.commondb.api.exc import LAST_HANDLED_EXCEPTION
from gen_epix.commondb.app_setup import create_fast_api
from gen_epix.commondb.config import AppCfg, BaseAppCfg
from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.commondb.test.test_client import TestClient
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.seqdb.api.router import create_routers
from gen_epix.seqdb.domain import command, enum, model
from gen_epix.seqdb.env import AppComposer


class SeqGenerationSettings(BaseModel):

    n_loci: int
    locus_length: int
    p_locus_deletion: float = 0.01
    p_nucleotide_substitution: float = 0.02
    p_nucleotide_deletion: float = 0.005
    seed: Optional[int] = 1001

    @field_validator(
        "p_locus_deletion",
        "p_nucleotide_substitution",
        "p_nucleotide_deletion",
    )
    @classmethod
    def _validate_probability(cls, p: float) -> float:
        if not 0.0 <= p < 1.0:
            raise ValueError("Probabilities must be in ]0,1[")
        return p

    @computed_field(  # type: ignore[prop-decorator]
        description="Total sequence length computed as n_loci * locus_length."
    )
    @cached_property
    def seq_length(self) -> int:
        return self.n_loci * self.locus_length

    @computed_field(  # type: ignore[prop-decorator]
        description="list of length n_loci with linear interpolated mutation probabilities over loci."
    )
    @cached_property
    def p_locus_mutation(self) -> list[float]:
        # linear interpolation of mutation probabilities over loci
        p_locus_mutation = [(i + 1) / (self.n_loci + 1) for i in range(self.n_loci)]
        # Deterministic shuffle based on provided seed
        _rng = random.Random(self.seed if self.seed is not None else 0)
        _rng.shuffle(p_locus_mutation)
        return p_locus_mutation

    @computed_field(  # type: ignore[prop-decorator]
        description="locus deletion probabilities computed as p_locus_mutation * p_locus_deletion."
    )
    @cached_property
    def p_locus_deletion_vec(self) -> list[float]:
        return [p * self.p_locus_deletion for p in self.p_locus_mutation]

    @computed_field(  # type: ignore[prop-decorator]
        description="per-nucleotide substitution probabilities computed as p_locus_mutation * p_nucleotide_substitution."
    )
    @cached_property
    def p_nucleotide_substitution_vec(self) -> list[float]:
        p_nucleotide_substitution_vec: list[float] = []
        for locus_idx in range(self.n_loci):
            for _ in range(self.locus_length):
                p_nucleotide_substitution_vec.append(
                    self.p_locus_mutation[locus_idx] * self.p_nucleotide_substitution
                )
        return p_nucleotide_substitution_vec

    @computed_field(  # type: ignore[prop-decorator]
        description="per-nucleotide deletion probabilities computed as p_locus_mutation * p_nucleotide_deletion."
    )
    @cached_property
    def p_nucleotide_deletion_vec(self) -> list[float]:
        p_nucleotide_deletion_vec: list[float] = []
        for locus_idx in range(self.n_loci):
            for _ in range(self.locus_length):
                p_nucleotide_deletion_vec.append(
                    self.p_locus_mutation[locus_idx] * self.p_nucleotide_deletion
                )
        return p_nucleotide_deletion_vec


class DistanceMatrix(BaseModel):

    model_config = {"arbitrary_types_allowed": True}

    obj_ids: list[UUID]
    matrix: np.ndarray


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
        )  # type: ignore[return-value]

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
        )  # type: ignore[return-value]

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
        )  # type: ignore[return-value]

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
        )  # type: ignore[return-value]

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
        )  # type: ignore[return-value]

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
        )  # type: ignore[return-value]

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
        )  # type: ignore[return-value]

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
        )  # type: ignore[return-value]

    def create_seq_distance_protocol(
        self,
        user_or_str: str | model.User,
        code: str,
        name: str | None = None,
        is_integer_distance: bool = True,
        seq_distance_protocol_type: enum.SeqDistanceProtocolType = enum.SeqDistanceProtocolType.KMER_EUCLIDEAN,
        max_stored_distance: float = 100.0,
    ) -> model.SeqDistanceProtocol:
        return self._create_protocol(
            model.SeqDistanceProtocol,
            user_or_str,
            code,
            name,
            is_integer_distance=is_integer_distance,  # Required field
            seq_distance_protocol_type=seq_distance_protocol_type,  # Required field - using KMER_EUCLIDEAN to avoid locus_set_id requirement
            max_stored_distance=max_stored_distance,  # Required field
        )  # type: ignore[return-value]

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
        )  # type: ignore[return-value]

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
        )  # type: ignore[return-value]

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
        )  # type: ignore[return-value]

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
        )  # type: ignore[assignment]
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
        )  # type: ignore[assignment]
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
        )  # type: ignore[return-value]

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
        )  # type: ignore[assignment]
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
        )  # type: ignore[assignment]
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
        return self._set_obj(seq)  # type: ignore[return-value]

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
        )  # type: ignore[assignment]
        user: model.User = self._get_obj(
            self.user_class, user_or_str
        )  # type: ignore[assignment]
        crud_command_class = self.app.domain.get_crud_command_for_model(protocol_class)
        protocol = self.app.handle(
            crud_command_class(
                operation=CrudOperation.CREATE_ONE,
                user=user,
                objs=protocol_class(
                    code=code, name=name if name else code, **kwargs
                ),  # type: ignore
            )
        )
        return self._set_obj(protocol)  # type: ignore[return-value]

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
            obj_id = (  # type: ignore[union-attr]
                self._get_obj(model_class, obj_or_str)  # type: ignore[assignment]
            ).id  # type: ignore[assignment]
        return obj_id

    @staticmethod
    def generate_random_sequences(
        n_seqs: int,
        settings: SeqGenerationSettings,
        assembly_protocol_id: UUID | None = None,
        locus_set_id: UUID | None = None,
        locus_detection_protocol_id: UUID | None = None,
    ) -> model.SampleBatchForUpload:
        # set IDs if not provided
        assembly_protocol_id = (
            assembly_protocol_id if assembly_protocol_id is not None else uuid.uuid4()
        )
        locus_set_id = locus_set_id if locus_set_id is not None else uuid.uuid4()
        locus_detection_protocol_id = (
            locus_detection_protocol_id
            if locus_detection_protocol_id is not None
            else uuid.uuid4()
        )
        # local RNG to  ensure reproducibility with same seed
        rng = random.Random(settings.seed)

        locus_ids: list[UUID] = [uuid.uuid4() for _ in range(settings.n_loci)]
        sequence: list[str] = [
            rng.choice(["A", "C", "G", "T"]) for _ in range(settings.seq_length)
        ]
        has_locus: list[bool] = [True] * settings.n_loci

        class SeqNode(BaseModel):
            sequence: list[str]
            has_locus: list[bool]

        children: list[SeqNode] = [SeqNode(sequence=sequence, has_locus=has_locus)]

        while len(children) < n_seqs:
            parent: SeqNode = children.pop(0)
            parent_sequence = parent.sequence
            parent_has_locus = parent.has_locus

            for _ in range(2):
                seq = parent_sequence.copy()
                has_locus = parent_has_locus.copy()
                # Apply locus deletions
                SeqdbTestClient._apply_locus_deletions(settings, rng, has_locus, seq)
                # Apply nucleotide substitutions
                SeqdbTestClient._apply_nucleotide_substitutions(
                    settings, rng, has_locus, seq
                )
                # Apply nucleotide deletions
                SeqdbTestClient._apply_nucleotide_deletions(
                    settings, rng, has_locus, seq
                )
                children.append(SeqNode(sequence=seq, has_locus=has_locus))

        seqs: list[str] = ["".join(node.sequence) for node in children]
        alleles: dict[str, model.AlleleForUpload] = {}
        samples_for_upload: list[model.SampleForUpload] = []
        for seq in seqs:  # type: ignore[assignment]
            seq_id: UUID = uuid.uuid4()
            allele_ids: list[UUID] = [NULL_ID] * settings.n_loci
            for locus_idx in range(settings.n_loci):
                locus_id = locus_ids[locus_idx]
                allele_seq = seq[
                    locus_idx
                    * settings.locus_length : (locus_idx + 1)
                    * settings.locus_length
                ]
                if set(allele_seq) != {"-"}:
                    if (
                        allele_seq in alleles  # type: ignore[comparison-overlap]
                        and alleles[allele_seq].locus_id != locus_id  # type: ignore[index]
                    ):
                        raise AssertionError(
                            "Allele sequence already exists for a different locus"
                        )
                    alleles[allele_seq] = model.AlleleForUpload(  # type: ignore[index]
                        seq="".join(x for x in allele_seq if x != "-"),
                        seq_format=enum.SeqFormat.STR_DNA,
                        locus_id=locus_id,
                    )
                    allele_ids[locus_idx] = alleles[allele_seq].id  # type: ignore[assignment,index]
            allele_profile_for_upload = model.AlleleProfileForUpload(
                locus_set_id=locus_set_id,
                locus_detection_protocol_id=locus_detection_protocol_id,
                allele_ids=allele_ids,  # type: ignore[arg-type]
                allele_profile_format=enum.AlleleProfileFormat.SORTED_ALLELE_IDS,
                seq_id=seq_id,
            )
            seq_for_upload = model.SeqForUpload(
                id=seq_id,
                contigs=[
                    model.Contig(
                        seq="".join(x for x in seq if x != "-"),
                        seq_format=enum.SeqFormat.STR_DNA,
                    )
                ],
                assembly_protocol_id=assembly_protocol_id,
            )
            samples_for_upload.append(
                model.SampleForUpload(
                    seqs=[seq_for_upload],
                    allele_profiles=[allele_profile_for_upload],
                )
            )
        sample_batch_for_upload = model.SampleBatchForUpload(
            samples=samples_for_upload,
            alleles=list(alleles.values()),
        )
        return sample_batch_for_upload

    @staticmethod
    def _apply_nucleotide_deletions(
        settings: SeqGenerationSettings,
        rng: random.Random,
        has_locus: list[bool],
        seq: list[str],
    ) -> None:
        for i in range(settings.seq_length):
            locus_idx = i // settings.locus_length
            if (
                has_locus[locus_idx]
                and rng.random() <= settings.p_nucleotide_deletion_vec[i]
            ):
                # Delete nucleotide
                seq[i] = "-"

    @staticmethod
    def _apply_nucleotide_substitutions(
        settings: SeqGenerationSettings,
        rng: random.Random,
        has_locus: list[bool],
        seq: list[str],
    ) -> None:
        for i in range(settings.seq_length):
            locus_idx = i // settings.locus_length
            if (
                has_locus[locus_idx]
                and rng.random() <= settings.p_nucleotide_substitution_vec[i]
            ):
                # Substitute nucleotide
                original_nuc = seq[i]
                if original_nuc != "-":
                    seq[i] = rng.choice([n for n in "ACGT" if n != original_nuc])

    @staticmethod
    def _apply_locus_deletions(
        settings: SeqGenerationSettings,
        rng: random.Random,
        has_locus: list[bool],
        seq: list[str],
    ) -> None:
        for i in range(settings.n_loci):
            if rng.random() <= settings.p_locus_deletion_vec[i]:
                # Delete locus
                has_locus[i] = False
                # update the sequence to have all gaps for that locus.
                for j in range(
                    i * settings.locus_length, (i + 1) * settings.locus_length
                ):
                    seq[j] = "-"

    @staticmethod
    def calculate_distance_matrix_from_allele_profiles(
        allele_profiles: list[model.AlleleProfile],
    ) -> DistanceMatrix:
        n_profiles = len(allele_profiles)

        if n_profiles == 0:
            return DistanceMatrix(
                obj_ids=[],
                matrix=np.array([[]]),
            )
        if n_profiles == 1:
            return DistanceMatrix(
                obj_ids=[allele_profiles[0].id],  # type: ignore[list-item]
                matrix=np.array([[0]]),
            )

        # Vector-Based Hamming Distance Computation
        # distance_matrix = np.zeros((n_profiles, n_profiles), dtype=int)
        # for i in range(n_profiles - 1):
        #     allele_ids = allele_profiles[i].get_allele_ids()
        #     for j in range(i + 1, n_profiles):
        #         other_allele_ids = allele_profiles[j].get_allele_ids()
        #         # Calculate hamming distance
        #         distance = np.count_nonzero(
        #             np.array(allele_ids) != np.array(other_allele_ids)
        #         )
        #         distance_matrix[i][j] = distance
        #         distance_matrix[j][i] = distance

        # p-dist approach
        # X = np.asarray(
        #     [
        #         allele_profile.get_allele_ids()
        #         for allele_profile in allele_profiles
        #     ]
        # )
        # distance_matrix = pdist(X, metric="hamming") * X.shape[1]

        # Categorical Hamming distance matrix one-hot encoding approach
        # per_sample_alleles_ids: list[list[UUID | None]] = [
        #     allele_profile.get_allele_ids() for allele_profile in allele_profiles
        # ]
        # # all profiles must share the same number of loci
        # n_loci = len(per_sample_alleles_ids[0])
        # for allele_ids in per_sample_alleles_ids:
        #     if len(allele_ids) != n_loci:
        #         raise ValueError(
        #             "All allele profiles must have the same number of loci"
        #         )

        # # prepare matrices to accumulate results
        # matches = np.zeros((n_profiles, n_profiles), dtype=np.int32)
        # comparable = np.zeros((n_profiles, n_profiles), dtype=np.int32)

        # # for each locus:
        # # - group samples by allele id
        # # - add 1 to matches for every pair in the same allele group
        # # - add 1 to comparable for every pair where both samples have any allele
        # for locus_idx in range(n_loci):
        #     groups: dict[UUID, list[int]] = {}
        #     present_indices: list[int] = []

        #     for sample_idx in range(n_profiles):
        #         allele_id = per_sample_alleles_ids[sample_idx][locus_idx]
        #         if allele_id is not None:
        #             present_indices.append(sample_idx)
        #             if allele_id not in groups:
        #                 groups[allele_id] = []
        #             groups[allele_id].append(sample_idx)

        #     # update matches, for each locus:
        #     # - retrieve the groups of samples sharing the same allele
        #     # - get the coordinates of the submatrix for each group
        #     # - add 1 to all those coordinates in the matches matrix
        #     for _, idx_list in groups.items():
        #         if len(idx_list) > 0:
        #             idx = np.asarray(idx_list, dtype=np.int32)
        #             matches[idx[:, None], idx[None, :]] += 1

        #     # update comparable, for each locus:
        #     # - determine if there are samples with an allele (data) at this locus (not None)
        #     # - get the coordinates of the submatrix for those samples
        #     # - add 1 to all those coordinates in the comparable matrix
        #     if len(present_indices) > 0:
        #         pidx = np.asarray(present_indices, dtype=np.int32)
        #         comparable[pidx[:, None], pidx[None, :]] += 1

        # # calculate distance matrix
        # distance_matrix = comparable - matches
        # np.fill_diagonal(distance_matrix, 0)

        # Sparse matrix approach
        per_sample_alleles_ids: list[list[UUID | None]] = [
            allele_profile.get_allele_ids() for allele_profile in allele_profiles
        ]
        n_loci = len(per_sample_alleles_ids[0])
        for allele_ids in per_sample_alleles_ids:
            if len(allele_ids) != n_loci:
                raise ValueError(
                    "All allele profiles must have the same number of loci"
                )

        matches = dok_matrix((n_profiles, n_profiles), dtype=np.int32)
        comparable = dok_matrix((n_profiles, n_profiles), dtype=np.int32)

        for locus_idx in range(n_loci):
            groups: dict[UUID, list[int]] = {}
            present_indices: list[int] = []

            for sample_idx in range(n_profiles):
                allele_id = per_sample_alleles_ids[sample_idx][locus_idx]
                if allele_id is not None:
                    present_indices.append(sample_idx)
                    if allele_id not in groups:
                        groups[allele_id] = []
                    groups[allele_id].append(sample_idx)

            for idx_list in groups.values():
                for i in idx_list:
                    for j in idx_list:
                        matches[i, j] += 1

            for i in present_indices:
                for j in present_indices:
                    comparable[i, j] += 1

        matches_dense = matches.toarray()
        comparable_dense = comparable.toarray()
        distance_matrix = comparable_dense - matches_dense
        np.fill_diagonal(distance_matrix, 0)

        return DistanceMatrix(
            obj_ids=[x.id for x in allele_profiles if x.id is not None],
            matrix=distance_matrix,
        )
