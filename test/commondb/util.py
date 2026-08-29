import json
import pickle
from pathlib import Path
from uuid import UUID

import numpy as np
import pandas as pd

from gen_epix.commondb.domain import model
from gen_epix.commondb.test.test_client import TestClient
from gen_epix.fastapp.enum import CrudOperation, OnException


def retrieve_db_data_from_file(
    test_client: TestClient,
    ordered_model_to_sheet_map: dict[type[model.Model], str],
    excel_file: Path,
    pickle_file: Path,
    extra_table_to_sheet_map: dict[str, str],
) -> dict[type[model.Model] | str, dict[UUID, model.Model] | pd.DataFrame]:
    is_loaded_from_pkl = False
    db: dict[type[model.Model] | str, dict[UUID, model.Model] | pd.DataFrame] = {}
    # Load from pickle if possible
    if (
        pickle_file.exists()
        and pickle_file.stat().st_mtime > excel_file.stat().st_mtime
    ):
        with open(pickle_file, "rb") as f:
            db = pickle.load(f)
        is_loaded_from_pkl = True

    # Load from excel if necessary
    if not is_loaded_from_pkl:
        for model_class, sheet_name in ordered_model_to_sheet_map.items():
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
            df.replace({np.nan: None}, inplace=True)
            # Handle JSON columns
            df = df.map(
                lambda x: (
                    {}
                    if x == "{}"
                    else (
                        json.loads(x)
                        if isinstance(x, str)
                        and len(x) > 1
                        and x[0] == "{"
                        and x[-1] == "}"
                        else x
                    )
                )
            )
            # Replace NaN with None
            df.replace({np.nan: None}, inplace=True)
            # Convert to models and put in db
            objs = [model_class(**x) for x in df.to_dict(orient="records")]  # type: ignore[misc]
            db[model_class] = {x.id: x for x in objs}  # type: ignore[misc]
        for table_name, sheet_name in extra_table_to_sheet_map.items():
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
            # Replace NaN with None
            df.replace({np.nan: None}, inplace=True)
            # Put in db
            db[table_name] = df
        with pickle_file.open("wb") as file_handle:
            pickle.dump(db, file_handle)

    # Get any root users in the to be loaded data
    user_class = [x for x in db if isinstance(x, type) and issubclass(x, model.User)][0]
    organization_class = [
        x for x in db if isinstance(x, type) and issubclass(x, model.Organization)
    ][0]
    root_role = test_client.app.user_manager._rbac_service.root_role
    df_root_users = [x for x in db[user_class].values() if root_role in x.roles]
    df_root_user: model.User | None = df_root_users[0] if df_root_users else None

    # Update existing root user and organization in test client to match the root user in the to be loaded data, if any
    root_user = test_client.get_root_user()
    if df_root_user:
        df_root_organization: model.Organization | None = db[organization_class][
            df_root_user.organization_id
        ]
        assert df_root_organization.id is not None
        env_db = test_client.app.user_manager._organization_service._repository._db
        organization_df: dict = env_db[organization_class]
        user_df: dict = env_db[user_class]
        env_db[organization_class].pop(root_user.organization_id)
        env_db[organization_class][df_root_organization.id] = df_root_organization
        env_db[user_class].pop(root_user.id)
        env_db[user_class][df_root_user.id] = df_root_user
        root_user = df_root_user

    # Populate the environment with the loaded data
    for model_class in ordered_model_to_sheet_map:
        df = db[model_class]
        objs = list(df.values())
        if issubclass(model_class, model.Organization):
            # Remove root organization from objs to create
            objs = [x for x in objs if x.id != root_user.organization_id]
        if issubclass(model_class, model.User):
            # Remove root user from objs to create
            objs = [x for x in objs if x.id != root_user.id]
        # Create the objects
        cmd = test_client.app.domain.get_crud_command_for_model(model_class)(
            user=root_user,
            operation=CrudOperation.CREATE_SOME,
            objs=objs,  # type: ignore[arg-type]
            on_id_set=OnException.IGNORE,
        )
        test_client.app.handle(cmd)
    for table_name in extra_table_to_sheet_map:
        test_client.props[table_name] = db[table_name]
    return db
