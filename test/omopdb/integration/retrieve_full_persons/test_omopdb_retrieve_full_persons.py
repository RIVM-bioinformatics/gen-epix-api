import logging
import uuid
from datetime import datetime, timezone
from test.omopdb.integration.retrieve_full_persons.base import (
    SKIP_ENDPOINTS,
    TEST_TYPE,
    VERBOSE,
)
from test.omopdb.omopdb_test_client import OmopdbTestClient as Env
from typing import ClassVar

import pytest

from gen_epix.commondb.domain import enum as commondb_enum
from gen_epix.commondb.domain.enum import AppType
from gen_epix.commondb.domain.util import get_app_cfgs
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.omopdb.domain import command, enum, model

OMOPDB_APP_CFGS = get_app_cfgs(
    AppType.OMOPDB,
    enum.ServiceType,
    enum.RepositoryType,
    TEST_TYPE,
)


@pytest.fixture(
    scope="module",
    name="env",
    params=[
        commondb_enum.DevRepositoryConfig.DICT_DEMO,
        commondb_enum.DevRepositoryConfig.SA_SQLITE_DEMO,
    ],
    ids=lambda x: x.value,
)
def env(
    request: pytest.FixtureRequest, tmp_path_factory: pytest.TempPathFactory
) -> Env:
    """Return a test client configured for either DICT or SA_SQLITE demo repos.

    The fixture is parameterized so the whole module runs against both
    repository backends. For the SA_SQLITE demo we respect `SKIP_ENDPOINTS`.
    """
    repo_cfg = request.param
    cfg_key = f"{TEST_TYPE.value}__{repo_cfg.value}"
    app_cfg = OMOPDB_APP_CFGS[cfg_key]

    # Create test directory to not affect subsequent runs (modifications of sqlite files)
    tmp_dir = tmp_path_factory.mktemp(f"retrieve_full_persons_{repo_cfg.value}")
    app_cfg.copy_repository_files(tmp_dir, on_exist="overwrite")

    # Ensure TestClient caching uses a unique name so a new client is created
    # and the copied repository files are used (avoids reusing a mutated client).
    unique_name = f"{app_cfg.name}__{uuid.uuid4().hex}"
    app_cfg._name = unique_name

    use_endpoints = (
        not SKIP_ENDPOINTS
        if repo_cfg == commondb_enum.DevRepositoryConfig.SA_SQLITE_DEMO
        else True
    )

    return Env.get_test_client(
        test_type=TEST_TYPE.value,
        app_cfg=app_cfg,
        verbose=VERBOSE,
        log_level=logging.ERROR,
        use_endpoints=use_endpoints,
    )


class TestRetrieveFullPersons:

    all_persons: ClassVar[list[model.Person]] = []
    test_persons: ClassVar[list[model.Person]] = []

    @pytest.fixture(scope="class", autouse=True)
    def _load_persons(self, request: pytest.FixtureRequest, env: Env) -> None:
        persons: list[model.Person] = env.handle(
            command.PersonCrudCommand(
                user=env.get_root_user(),
                obj_ids=None,
                operation=CrudOperation.READ_ALL,
            ),
            use_endpoint=False,
        )
        assert persons

        request.cls.all_persons = persons
        request.cls.test_persons = persons[:10]

    def test_retrieve_full_persons_by_ids(self, env: Env) -> None:
        person_ids = [
            person.person_id
            for person in self.test_persons
            if person.person_id is not None
        ]
        assert person_ids

        full_persons: list[model.FullPerson] = env.handle(
            command.RetrieveFullPersonsCommand(
                user=env.get_root_user(),
                person_ids=person_ids,
            ),
            use_endpoint=False,
        )

        assert len(full_persons) == len(person_ids)
        assert all(isinstance(person, model.FullPerson) for person in full_persons)
        assert [person.person_id for person in full_persons] == person_ids

        full_persons_by_id = {person.person_id: person for person in full_persons}

        for person in self.test_persons[:2]:
            assert person.person_id is not None
            assert (
                full_persons_by_id[person.person_id].year_of_birth
                == person.year_of_birth
            )
            assert isinstance(full_persons_by_id[person.person_id].observations, list)
            assert isinstance(full_persons_by_id[person.person_id].measurements, list)

    # def test_retrieve_full_persons_by_modified_range(self, env: Env) -> None:
    #     assert len(self.test_persons) >= 2

    #     first_person = self.test_persons[0].model_copy()
    #     second_person = self.test_persons[1]
    #     assert first_person.person_id is not None
    #     assert second_person.person_id is not None

    #     first_person.year_of_birth += 1

    #     updated_first_person: model.Person = env.handle(
    #         command.PersonCrudCommand(
    #             user=env.get_root_user(),
    #             operation=CrudOperation.UPDATE_ONE,
    #             objs=first_person,
    #         ),
    #         use_endpoint=False,
    #     )
    #     assert updated_first_person.person_id is not None

    #     refreshed_persons: list[model.Person] = env.handle(
    #         command.PersonCrudCommand(
    #             user=env.get_root_user(),
    #             operation=CrudOperation.READ_SOME,
    #             obj_ids=[updated_first_person.person_id, second_person.person_id],
    #         ),
    #         use_endpoint=False,
    #     )
    #     persons_by_id = {x.person_id: x for x in refreshed_persons}

    #     first_modified_at = persons_by_id[updated_first_person.person_id].modified_at
    #     second_modified_at = second_person.modified_at

    #     assert first_modified_at is not None
    #     assert second_modified_at is not None
    #     assert first_modified_at != second_modified_at

    #     target_start = first_modified_at - timedelta(seconds=1)
    #     target_end = first_modified_at + timedelta(seconds=1)

    #     full_persons: list[model.FullPerson] = env.handle(
    #         command.RetrieveFullPersonsCommand(
    #             user=env.get_root_user(),
    #             modified_since=target_start,
    #             modified_until=target_end,
    #         ),
    #         use_endpoint=False,
    #     )

    #     assert len(full_persons) == 1
    #     assert all(isinstance(person, model.FullPerson) for person in full_persons)
    #     assert full_persons[0].person_id == updated_first_person.person_id
    #     assert full_persons[0].year_of_birth == updated_first_person.year_of_birth

    def test_retrieve_full_persons_with_ids_and_modified_range_raises(
        self, env: Env
    ) -> None:
        root_user = env.get_root_user()
        with pytest.raises(
            ValueError,
            match="Cannot provide both person_ids and modified_since/modified_until",
        ):
            env.handle(
                command.RetrieveFullPersonsCommand(
                    user=root_user,
                    person_ids=[env.generate_id()],
                    modified_since=datetime(2026, 1, 1, tzinfo=timezone.utc),
                    modified_until=datetime(2026, 1, 2, tzinfo=timezone.utc),
                ),
                use_endpoint=False,
            )

    def test_retrieve_full_persons_with_duplicate_ids(self, env: Env) -> None:
        root_user = env.get_root_user()
        duplicate_person_id = env.generate_id()

        with pytest.raises(ValueError, match="person_ids must be unique"):
            env.handle(
                command.RetrieveFullPersonsCommand(
                    user=root_user,
                    person_ids=[duplicate_person_id, duplicate_person_id],
                ),
                use_endpoint=False,
            )
