from collections.abc import Iterable
from collections.abc import Set as AbstractSet
from datetime import datetime
from typing import Any, cast
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.orm import Session

import gen_epix.seqdb.repositories.sa_model as sa_model
from gen_epix.fastapp import BaseUnitOfWork
from gen_epix.fastapp.repositories import SARepository, SAUnitOfWork
from gen_epix.seqdb.domain import enum, exc, model
from gen_epix.seqdb.domain.repository import BaseSeqRepository


class SeqSARepository(SARepository, BaseSeqRepository):

    def get_sample_ids_modified_in_range(
        self,
        uow: BaseUnitOfWork,
        modified_since: datetime | None = None,
        modified_until: datetime | None = None,
    ) -> list[UUID]:
        assert isinstance(uow, SAUnitOfWork)
        modified_sample_ids: set[UUID] = set()
        for model_class in [model.Sample] + model.FullSample.DATA_CLASSES:
            sa_model_class = sa_model.SA_MODELS_BY_SERVICE_TYPE[enum.ServiceType.SEQ][
                model_class
            ]
            if model_class == model.Sample:
                id_field = sa_model_class.id  # type: ignore[attr-defined]
            else:
                id_field = sa_model_class.sample_id  # type: ignore[attr-defined]
            conditions = []
            if modified_since is not None:
                conditions.append(sa_model_class.modified_at >= modified_since)  # type: ignore[attr-defined]
            if modified_until is not None:
                conditions.append(sa_model_class.modified_at < modified_until)  # type: ignore[attr-defined]
            stmt = sa.select(id_field).where(*conditions)
            modified_sample_ids.update(row[0] for row in uow.session.execute(stmt))
        return sorted(modified_sample_ids)

    def get_full_samples_by_sample_ids(
        self,
        sample_ids: list[UUID],
    ) -> list[model.FullSample]:
        if not sample_ids:
            return []

        # Initialize some
        sample_id_set = set(sample_ids)
        model_classes = (
            [model.Sample, model.SampleIdentifier]
            + model.FullSample.DATA_CLASSES
            + model.FullSample.IDENTIFIER_CLASSES
        )
        db: dict[type[model.Model], dict[UUID, list[model.Model]]] = {
            model_class: {sample_id: [] for sample_id in sample_ids}
            for model_class in model_classes
        }

        # Retrieve all data and create FullSamples
        with self.uow() as uow:
            assert isinstance(uow, SAUnitOfWork)
            # Retrieve all data per sample
            for model_class in model_classes:
                sa_model_class = sa_model.SA_MODELS_BY_SERVICE_TYPE[
                    enum.ServiceType.SEQ
                ][model_class]
                if model_class == model.Sample:
                    id_field_name = "id"
                elif model_class in model.FullSample.DATA_CLASSES:
                    id_field_name = "sample_id"
                else:
                    id_field_name = "internal_id"
                id_field = getattr(sa_model_class, id_field_name)  # type: ignore[attr-defined]
                stmt: sa.Select = sa.select(sa_model_class).where(
                    id_field.in_(sample_id_set)  # type: ignore[attr-defined]
                )
                mapper = self.get_mapper(model_class)
                objs_by_sample = db[model_class]
                for row in uow.session.execute(stmt):
                    obj = cast(model.Model, mapper.load(row[0]))
                    sample_id = cast(UUID, getattr(obj, id_field_name))
                    objs_by_sample[sample_id].append(obj)

            # Create FullSamples
            class_field_map = (
                model.FullSample.DATA_CLASS_FIELD_MAP
                | model.FullSample.IDENTIFIER_FIELD_MAP
                | {model.SampleIdentifier: "sample_identifiers"}
            )
            full_samples: list[model.FullSample] = []
            for sample_id in sample_ids:
                samples = db[model.Sample][sample_id]
                if not samples:
                    continue
                sample = cast(model.Sample, samples[0])
                full_sample_kwargs = {}
                for model_class, field_name in class_field_map.items():
                    full_sample_kwargs[field_name] = db[model_class][sample_id]
                full_samples.append(
                    model.FullSample(
                        id=sample_id,
                        sample=sample,
                        **full_sample_kwargs,  # type: ignore[arg-type]
                    )
                )

            return full_samples

    def get_sample_identifiers_by_sample_ids(
        self,
        sample_ids: list[UUID],
    ) -> list[model.SampleIdentifier]:
        if not sample_ids:
            return []
        sa_model_class = sa_model.SA_MODELS_BY_SERVICE_TYPE[enum.ServiceType.SEQ][
            model.SampleIdentifier
        ]
        stmt: sa.Select = sa.select(sa_model_class).where(
            sa_model_class.internal_id.in_(set(sample_ids))  # type: ignore[attr-defined]
        )
        mapper = self.get_mapper(model.SampleIdentifier)
        with self.uow() as uow:
            assert isinstance(uow, SAUnitOfWork)
            return [
                cast(model.SampleIdentifier, mapper.load(row[0]))
                for row in uow.session.execute(stmt)
            ]

    def retrieve_seq_fasta(
        self,
        uow: BaseUnitOfWork,
        seq_ids: list[UUID],
    ) -> Iterable[tuple[UUID, list[tuple[UUID, str]]]]:
        self.raise_on_duplicate_ids(seq_ids)
        assert isinstance(uow, SAUnitOfWork)
        mapper = self.get_mapper(model.Seq)
        stmt = sa.select(sa_model.Seq).where(sa_model.Seq.id.in_(seq_ids))
        result = uow.session.execute(stmt)
        for row in result:
            seq: model.Seq = mapper.load(row[0])  # type: ignore[assignment]
            contig_list: list[tuple[UUID, str]] = []
            for contig in seq.contigs:
                if contig.seq_format != enum.SeqFormat.STR_DNA:
                    raise exc.InitializationServiceError(
                        "6672c6dd",
                        f"FASTA export not supported for {contig.seq_format.value} format",
                    )
                assert contig.id is not None
                contig_list.append((contig.id, contig.seq))
            assert seq.id is not None
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
        seq_distance_model: Any = sa_model.SeqDistance
        stmt = sa.select(
            seq_distance_model.id,
            seq_distance_model.format,
            seq_distance_model.content,
            seq_distance_model.content2,
        ).where(
            (seq_distance_model.protocol_id == protocol_id)
            & seq_distance_model.seq_profile_id.in_(profile_ids)
        )
        assert isinstance(uow, SAUnitOfWork)
        result_iterator = uow.session.execute(stmt)
        matching_profile_ids: set[UUID] = set()
        for row in result_iterator:
            distance_format: enum.SeqDistanceFormat = row[1]
            distances: str = row[2]
            distances2: str | None = row[3]
            BaseSeqRepository._get_matching_profiles_for_distance_dict_format(
                max_distance,
                matching_profile_ids,
                distance_format,
                distances,
                distances2=distances2,
            )

        return list(matching_profile_ids - set(profile_ids))

    @staticmethod
    def _create_profile_filter_temp_table(
        session: Session,
        profile_ids: list[UUID],
    ) -> sa.Table:
        """Create a temp table for seq_profile_id filtering.

        IN() on uniqueidentifier FK columns via pyodbc raises ODBC 07002
        regardless of list size; a temp-table JOIN avoids the parameter
        binding entirely. Only called on mssql dialects.
        """
        temp_name = f"#sdist_{uuid4().hex}"
        col_name = "seq_profile_id"
        col_type = sa_model.SeqDistance.__table__.c[col_name].type
        dialect = session.get_bind().dialect
        col_sql = col_type.compile(dialect=dialect)
        temp_table = sa.Table(
            temp_name,
            sa_model.SeqDistance.metadata,
            sa.Column(col_name, col_type),
        )
        session.execute(
            sa.text(f"CREATE TABLE {temp_name} ({col_name} {col_sql})")
        )
        batch_size = 1000
        for i in range(0, len(profile_ids), batch_size):
            values = [
                {col_name: pid}
                for pid in profile_ids[i : i + batch_size]
            ]
            session.execute(sa.insert(temp_table), values)
            session.flush()
        return temp_table

    def iter_seq_distances(
        self,
        uow: BaseUnitOfWork,
        protocol_id: UUID,
        profile_ids: list[UUID] | None = None,
    ) -> Iterable[model.SeqDistance]:
        assert isinstance(uow, SAUnitOfWork)
        stmt = sa.select(sa_model.SeqDistance).where(
            sa_model.SeqDistance.protocol_id == protocol_id
        )
        if profile_ids is not None:
            if not profile_ids:
                return  # IN() with empty list is invalid SQL Server syntax
            if uow.session.get_bind().dialect.name == "mssql":
                temp_table = self._create_profile_filter_temp_table(
                    uow.session, profile_ids
                )
                stmt = stmt.join(
                    temp_table,
                    sa_model.SeqDistance.seq_profile_id
                    == temp_table.c.seq_profile_id,
                )
            else:
                stmt = stmt.where(
                    sa_model.SeqDistance.seq_profile_id.in_(profile_ids)
                )
        mapper = self.get_mapper(model.SeqDistance)
        result_iterator = uow.session.execute(stmt)
        for row in result_iterator:
            sa_seq_distance: sa_model.SeqDistance = row[0]
            seq_distance: model.SeqDistance = mapper.load(sa_seq_distance)  # type: ignore[assignment]
            yield seq_distance

    def iter_seq_distance_profile_ids(
        self,
        uow: BaseUnitOfWork,
        protocol_id: UUID,
    ) -> Iterable[UUID]:
        stmt = (
            sa.select(sa_model.SeqDistance.seq_profile_id)
            .distinct()
            .where(sa_model.SeqDistance.protocol_id == protocol_id)
        )
        assert isinstance(uow, SAUnitOfWork)
        for row in uow.session.execute(stmt):
            yield row[0]

    def get_max_seq_distance_modified_at(
        self,
        uow: BaseUnitOfWork,
        protocol_id: UUID,
    ) -> datetime | None:
        stmt = sa.select(sa.func.max(sa_model.SeqDistance.modified_at)).where(
            sa_model.SeqDistance.protocol_id == protocol_id
        )
        assert isinstance(uow, SAUnitOfWork)
        return uow.session.execute(stmt).scalar()

    def get_profiles_by_protocol_ids(
        self,
        uow: BaseUnitOfWork,
        protocol_ids: list[UUID],
    ) -> list[model.SeqProfile]:
        stmt = sa.select(sa_model.SeqProfile).where(
            sa_model.SeqProfile.protocol_id.in_(protocol_ids)
        )
        mapper = self.get_mapper(model.SeqProfile)
        assert isinstance(uow, SAUnitOfWork)
        result: list[model.SeqProfile] = []
        for row in uow.session.execute(stmt):
            result.append(mapper.load(row[0]))  # type: ignore[arg-type]
        return result

    def filter_seq_profiles_by_quality(
        self,
        uow: BaseUnitOfWork,
        seq_profile_ids: list[UUID],
        allowed_qc_results: AbstractSet[
            enum.QualityControlResult
        ] = enum.QualityControlResultSet.USABLE.value,
    ) -> list[UUID]:

        if not seq_profile_ids or not allowed_qc_results:
            return []
        stmt = sa.select(sa_model.SeqProfile.id).where(
            (sa_model.SeqProfile.id.in_(seq_profile_ids))
            & sa_model.SeqProfile.qc_result.in_(allowed_qc_results)
        )
        assert isinstance(uow, SAUnitOfWork)
        retval: list[UUID] = uow.session.execute(stmt).scalars().all()  # type: ignore[assignment]
        return retval
