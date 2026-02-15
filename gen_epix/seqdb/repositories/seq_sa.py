from collections.abc import Iterable
from typing import Any
from uuid import UUID

import sqlalchemy as sa

from gen_epix.fastapp import BaseUnitOfWork
from gen_epix.fastapp.repositories import SARepository, SAUnitOfWork
from gen_epix.seqdb.domain import enum, exc, model
from gen_epix.seqdb.domain.repository import BaseSeqRepository
from gen_epix.seqdb.repositories import sa_model


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
        for sa_seq in result:
            seq: model.Seq = mapper.load(sa_seq)  # type: ignore[assignment]
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
        seq_distance_protocol_id: UUID,
        profile_ids: list[UUID],
        max_distance: float,
        **kwargs: Any,
    ) -> list[UUID]:
        if not profile_ids:
            return []
        stmt = sa.select(
            sa_model.SeqDistance.id,
            sa_model.SeqDistance.distances,
            sa_model.SeqDistance.distance_format,
        ).where(
            (sa_model.SeqDistance.seq_distance_protocol_id == seq_distance_protocol_id)
            & sa_model.SeqDistance.profile_id.in_(profile_ids)
        )
        assert isinstance(uow, SAUnitOfWork)
        result_iterator = uow.session.execute(stmt)
        matching_profile_ids: set[UUID] = set()
        for row in result_iterator:
            distances: str = row[1]
            distance_format: enum.SeqDistanceFormat = row[2]
            BaseSeqRepository._get_matching_profiles_for_distance_dict_format(
                max_distance, matching_profile_ids, distances, distance_format
            )

        return list(matching_profile_ids - set(profile_ids))
