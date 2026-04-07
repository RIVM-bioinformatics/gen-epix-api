from collections.abc import Iterable
from datetime import datetime
from typing import Any
from uuid import UUID

import sqlalchemy as sa

import gen_epix.seqdb.repositories.sa_model.seq as sa_model
from gen_epix.fastapp import BaseUnitOfWork
from gen_epix.fastapp.repositories import SARepository, SAUnitOfWork
from gen_epix.seqdb.domain import enum, exc, model
from gen_epix.seqdb.domain.repository import BaseSeqRepository


class SeqSARepository(SARepository, BaseSeqRepository):

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
                        f"FASTA export not supported for {contig.seq_format.value} format"
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
        stmt = sa.select(
            sa_model.SeqDistance.id,
            sa_model.SeqDistance.format,
            sa_model.SeqDistance.content,
            sa_model.SeqDistance.content2,
        ).where(
            (sa_model.SeqDistance.protocol_id == protocol_id)
            & sa_model.SeqDistance.seq_profile_id.in_(profile_ids)
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

    def iter_seq_distances(
        self,
        uow: BaseUnitOfWork,
        protocol_id: UUID,
    ) -> Iterable[model.SeqDistance]:
        stmt = sa.select(sa_model.SeqDistance).where(
            sa_model.SeqDistance.protocol_id == protocol_id
        )
        mapper = self.get_mapper(model.SeqDistance)
        assert isinstance(uow, SAUnitOfWork)
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
        stmt = sa.select(sa.func.distinct(sa_model.SeqDistance.seq_profile_id)).where(
            sa_model.SeqDistance.protocol_id == protocol_id
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

    def get_filtered_seq_profiles_by_quality(
        self,
        uow: BaseUnitOfWork,
        seq_profile_ids: list[UUID],
    ) -> list[UUID]:
        if not seq_profile_ids:
            return []
        stmt = sa.select(sa_model.SeqProfile.id).where(
            (sa_model.SeqProfile.id.in_(seq_profile_ids))
            & sa.or_(
                sa_model.SeqProfile.qc_result == enum.QualityControlResult.PASS,
                sa_model.SeqProfile.qc_result == enum.QualityControlResult.PENDING,
            )
        )
        mapper = self.get_mapper(model.SeqProfile)
        assert isinstance(uow, SAUnitOfWork)
        result: list[UUID] = []
        for row in uow.session.execute(stmt):
            result.append(mapper.load(row[0]).id)  # type: ignore[attr-defined]
        return result
