from collections.abc import Iterable
from collections.abc import Set as AbstractSet
from datetime import datetime
from typing import Any
from uuid import UUID

from gen_epix.fastapp.repositories import DictRepository
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork
from gen_epix.seqdb.domain import enum, exc, model
from gen_epix.seqdb.domain.repository import BaseSeqRepository


class SeqDictRepository(DictRepository, BaseSeqRepository):

    def get_sample_ids_modified_in_range(
        self,
        uow: BaseUnitOfWork,
        modified_since: datetime | None = None,
        modified_until: datetime | None = None,
    ) -> list[UUID]:
        modified_since = modified_since or datetime.min
        modified_until = modified_until or datetime.max
        modified_sample_ids: set[UUID] = set()
        for model_class in [model.Sample] + model.FullSample.DATA_CLASSES:
            if model_class == model.Sample:
                id_field_name = "id"
            else:
                id_field_name = "sample_id"
            for obj in self.db[model_class].values():
                assert isinstance(obj, model_class)
                sample_id: UUID = getattr(obj, id_field_name)
                modified_at: datetime = obj.modified_at  # type: ignore[attr-defined]
                if modified_at < modified_since:
                    continue
                if modified_at >= modified_until:
                    continue
                modified_sample_ids.add(sample_id)
        return sorted(modified_sample_ids)

    def get_full_samples_by_sample_ids(
        self,
        sample_ids: list[UUID],
    ) -> list[model.FullSample]:
        """See parent class method"""
        # Retrieve all data per sample
        sample_id_set = set(sample_ids)
        model_classes = (
            model.FullSample.DATA_CLASSES
            + list(model.FullSample.IDENTIFIER_CLASSES)
            + [model.SampleIdentifier]
        )
        db: dict[model.Model, dict[UUID, list[model.Model]]] = {  # type: ignore[assignment]
            x: {y: [] for y in sample_ids} for x in model_classes  # type: ignore[misc]
        }
        for model_class in model_classes:
            objs_by_sample = db[model_class]  # type: ignore[index]
            if model_class == model.Sample:
                id_field_name = "id"
            elif model_class in model.FullSample.DATA_CLASSES:
                id_field_name = "sample_id"
            else:
                id_field_name = "internal_id"
            for obj in self.db[model_class].values():
                sample_id: UUID = getattr(obj, id_field_name)  # type: ignore[assignment]
                if sample_id in sample_id_set:  # type: ignore[union-attr]
                    objs_by_sample[sample_id].append(obj)  # type: ignore[arg-type]

        # Create FullSamples
        full_samples: list[model.FullSample] = []
        class_field_map = (
            model.FullSample.DATA_CLASS_FIELD_MAP
            | model.FullSample.IDENTIFIER_FIELD_MAP
            | {model.SampleIdentifier: "sample_identifiers"}
        )
        for sample_id in sample_ids:
            sample: model.Sample = self.db[model.Sample][sample_id]  # type: ignore[assignment]
            full_sample_kwargs = {}
            for model_class, field_name in class_field_map.items():
                full_sample_kwargs[field_name] = db[model_class][sample_id]  # type: ignore[index,arg-type]
            full_samples.append(
                model.FullSample(
                    id=sample_id,
                    sample=sample,
                    **full_sample_kwargs,  # type: ignore[arg-type]
                )
            )
        return full_samples

    def retrieve_seq_fasta(
        self,
        uow: BaseUnitOfWork,
        seq_ids: list[UUID],
    ) -> Iterable[tuple[UUID, list[tuple[UUID, str]]]]:
        self.raise_on_duplicate_ids(seq_ids)

        seqs: list[model.Seq] = self.read_some(model.Seq, seq_ids)  # type: ignore[assignment]
        for seq in seqs:
            assert seq.id is not None
            contig_list: list[tuple[UUID, str]] = []
            for contig in seq.contigs:
                if contig.seq_format != enum.SeqFormat.STR_DNA:
                    raise exc.InitializationServiceError(
                        f"FASTA export not supported for {contig.seq_format.value} format"
                    )
                assert contig.id is not None
                contig_list.append((contig.id, contig.seq))
            yield (seq.id, contig_list)

    def retrieve_similar_profiles(
        self,
        uow: BaseUnitOfWork,
        protocol_id: UUID,
        profile_ids: list[UUID],
        max_distance: float,
        **kwargs: Any,
    ) -> list[UUID]:
        if not profile_ids:
            return []

        profile_id_set = set(profile_ids)
        table: dict[UUID, model.SeqDistance] = self.db[  # type: ignore[assignment]
            model.SeqDistance
        ]
        matching_profile_ids: set[UUID] = set()
        for seq_distance in table.values():
            if seq_distance.protocol_id != protocol_id:
                continue
            if seq_distance.seq_profile_id not in profile_id_set:
                continue
            # Each seq_distance corresponds to one profile_id
            BaseSeqRepository._get_matching_profiles_for_distance_dict_format(
                max_distance,
                matching_profile_ids,
                seq_distance.format,
                seq_distance.content,
                distances2=seq_distance.content2,
            )

        return list(matching_profile_ids - profile_id_set)

    def iter_seq_distances(
        self,
        uow: BaseUnitOfWork,
        protocol_id: UUID,
    ) -> Iterable[model.SeqDistance]:
        table: dict[UUID, model.SeqDistance] = self.db[  # type: ignore[assignment]
            model.SeqDistance
        ]
        for seq_distance in table.values():
            if seq_distance.protocol_id == protocol_id:
                yield seq_distance

    def iter_seq_distance_profile_ids(
        self,
        uow: BaseUnitOfWork,
        protocol_id: UUID,
    ) -> Iterable[UUID]:
        # table: dict[UUID, model.SeqDistance] = self.db[  # type: ignore[assignment]
        #     model.SeqDistance
        # ]
        seen: set[UUID] = set()
        # for seq_distance in table.values():
        for seq_distance in self.iter_seq_distances(uow, protocol_id):
            if seq_distance.seq_profile_id not in seen:
                seen.add(seq_distance.seq_profile_id)
                yield seq_distance.seq_profile_id

    def get_max_seq_distance_modified_at(
        self,
        uow: BaseUnitOfWork,
        protocol_id: UUID,
    ) -> datetime | None:
        df: dict[UUID, model.SeqDistance] = self.db[  # type: ignore[assignment]
            model.SeqDistance
        ]
        maximum_modified_timestamp: datetime | None = None
        for seq_distance in df.values():
            if seq_distance.protocol_id == protocol_id:
                if seq_distance.modified_at is not None and (
                    maximum_modified_timestamp is None
                    or seq_distance.modified_at > maximum_modified_timestamp
                ):
                    maximum_modified_timestamp = seq_distance.modified_at
        return maximum_modified_timestamp

    def get_profiles_by_protocol_ids(
        self,
        uow: BaseUnitOfWork,
        protocol_ids: list[UUID],
    ) -> list[model.SeqProfile]:
        unique_protocol_ids = set(protocol_ids)
        df: dict[UUID, model.SeqProfile] = self.db[  # type: ignore[assignment]
            model.SeqProfile
        ]
        return [x for x in df.values() if x.protocol_id in unique_protocol_ids]

    def filter_seq_profiles_by_quality(
        self,
        uow: BaseUnitOfWork,
        seq_profile_ids: list[UUID],
        allowed_qc_results: AbstractSet[
            enum.QualityControlResult
        ] = enum.QualityControlResultSet.USABLE.value,
    ) -> list[UUID]:
        unique_profile_ids = set(seq_profile_ids)
        df: dict[UUID, model.SeqProfile] = self.db[  # type: ignore[assignment]
            model.SeqProfile
        ]
        return [
            x.id
            for x in df.values()
            if x.id is not None
            and x.id in unique_profile_ids
            and x.qc_result is not None
            and x.qc_result in allowed_qc_results
        ]
