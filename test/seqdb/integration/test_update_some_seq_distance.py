"""Integration test for SeqSARepository.update_some_seq_distance_content.

Verifies that update_some_seq_distance_content writes content changes
to a real SA_SQLITE database via SQLAlchemy Core executemany.
"""

import json
import warnings
from test.seqdb.performance.calculate_seq_distances.generate_seqdb_models import (
    generate_scale_test_db,
)
from test.seqdb.performance.common import (
    create_dict_repository,
    create_sqlite_repository,
    fill_empty_sqlite_repository,
)
from uuid import UUID, uuid4

import pytest

from gen_epix.fastapp import CrudOperation
from gen_epix.fastapp.domain.entity import Entity
from gen_epix.seqdb.domain import DOMAIN
from gen_epix.seqdb.domain import enum as seqdb_enum
from gen_epix.seqdb.domain import model


@pytest.mark.scenario_ids("TC-11-13-01")
class TestBulkUpdateSeqDistanceContentSA:
    """Verify update_some_seq_distance_content against a real SA_SQLITE database."""

    @pytest.fixture(scope="class")
    def sa_repo_with_data(self, tmp_path_factory: pytest.TempPathFactory):  # type: ignore[type-arg]
        tmp_path = tmp_path_factory.mktemp("update_some_seq_distance")
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            entities: list[Entity] = DOMAIN.get_dag_sorted_entities(
                service_type=seqdb_enum.ServiceType.SEQ,
                persistable=True,
            )
        user_id = UUID("00000000-0000-0000-0000-000000000001")
        db = generate_scale_test_db(n_loci=3, n_existing=3, seed=42)
        dict_repo = create_dict_repository(pickle_file=None, db=db, entities=entities)
        sa_repo = create_sqlite_repository(
            empty_sa_sqlite_file=tmp_path / "test.sqlite",
            entities=entities,
            recreate_sqlite_file=True,
        )
        fill_empty_sqlite_repository(dict_repo, sa_repo, entities, user_id)
        return sa_repo, user_id

    def test_content_updated_in_sqlite(self, sa_repo_with_data) -> None:  # type: ignore[no-untyped-def]
        sa_repo, user_id = sa_repo_with_data

        with sa_repo.uow() as uow:
            existing: list[model.SeqDistance] = sa_repo.crud(
                uow, user_id, model.SeqDistance, CrudOperation.READ_ALL
            )
        assert len(existing) == 3

        # Content must be a PROFILE_DISTANCE_MAP: keys are UUID strings.
        sentinel_id = str(uuid4())
        new_content = json.dumps({sentinel_id: 99.0})
        for sd in existing:
            sd.content = new_content

        with sa_repo.uow() as uow:
            sa_repo.update_some_seq_distance_content(uow, user_id, existing)

        with sa_repo.uow() as uow:
            read_back: list[model.SeqDistance] = sa_repo.crud(
                uow, user_id, model.SeqDistance, CrudOperation.READ_ALL
            )
        assert len(read_back) == 3
        for sd in read_back:
            assert json.loads(sd.content) == {sentinel_id: 99.0}

    def test_partial_update_only_modifies_specified_records(
        self, sa_repo_with_data
    ) -> None:
        sa_repo, user_id = sa_repo_with_data

        # Read current state (content set by previous test)
        with sa_repo.uow() as uow:
            all_records: list[model.SeqDistance] = sa_repo.crud(
                uow, user_id, model.SeqDistance, CrudOperation.READ_ALL
            )
        assert len(all_records) == 3

        # Only update the first record; keys must be UUID strings (PROFILE_DISTANCE_MAP).
        target = all_records[0]
        partial_id = str(uuid4())
        target.content = json.dumps({partial_id: 1.0})
        unchanged_content = {
            sd.id: sd.content for sd in all_records if sd.id != target.id
        }
        with sa_repo.uow() as uow:
            sa_repo.update_some_seq_distance_content(uow, user_id, [target])

        with sa_repo.uow() as uow:
            read_back: list[model.SeqDistance] = sa_repo.crud(
                uow, user_id, model.SeqDistance, CrudOperation.READ_ALL
            )
        read_back_by_id = {sd.id: sd for sd in read_back}
        assert json.loads(read_back_by_id[target.id].content) == {partial_id: 1.0}
        for sd_id, original in unchanged_content.items():
            assert read_back_by_id[sd_id].content == original
