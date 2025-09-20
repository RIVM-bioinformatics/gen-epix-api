import json
import pickle
from pathlib import Path
from typing import Type
from uuid import UUID

import numpy as np
import pandas as pd

from gen_epix.commondb.domain import model
from gen_epix.commondb.test.test_client import TestClient
from gen_epix.fastapp.enum import CrudOperation


def retrieve_db_data_from_file(
    test_client: TestClient,
    ordered_model_to_sheet_map: dict[Type[model.Model], str],
    excel_file: Path,
    pickle_file: Path,
    extra_table_to_sheet_map: dict[str, str],
) -> dict[Type[model.Model] | str, dict[UUID, model.Model] | pd.DataFrame]:
    is_loaded_from_pkl = False
    db: dict[Type[model.Model] | str, dict[UUID, model.Model] | pd.DataFrame] = {}
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
            df.replace({np.nan: None}, inplace=True)
            objs = [model_class(**x) for x in df.to_dict(orient="records")]  # type: ignore[misc]
            db[model_class] = {x.id: x for x in objs}  # type: ignore[misc]
        for table_name, sheet_name in extra_table_to_sheet_map.items():
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
            df.replace({np.nan: None}, inplace=True)
            db[table_name] = df
        with pickle_file.open("wb") as file_handle:
            pickle.dump(db, file_handle)

    # Populate the environment with the loaded data
    root_user = test_client.get_root_user()
    for model_class in ordered_model_to_sheet_map:
        df = db[model_class]
        objs = list(df.values())
        if issubclass(model_class, model.Organization):
            # Update the root organization
            cmd = test_client.app.domain.get_crud_command_for_model(model_class)(
                user=root_user,
                operation=CrudOperation.UPDATE_ONE,
                objs=[x for x in objs if x.id == root_user.organization_id][0],
            )
            test_client.app.handle(cmd)
            # Remove root organization from objs to create
            objs = [x for x in objs if x.id != root_user.organization_id]
        if issubclass(model_class, model.User):
            # Update the root user
            cmd = test_client.app.domain.get_crud_command_for_model(model_class)(
                user=root_user,
                operation=CrudOperation.UPDATE_ONE,
                objs=[x for x in objs if x.id == root_user.id][0],
            )
            test_client.app.handle(cmd)
            # Remove root user from objs to create
            objs = [x for x in objs if x.id != root_user.id]
        # Create the objects
        cmd = test_client.app.domain.get_crud_command_for_model(model_class)(
            user=root_user,
            operation=CrudOperation.CREATE_SOME,
            objs=objs,  # type: ignore[arg-type]
            props={"id_present": "keep"},
        )
        test_client.app.handle(cmd)
    for table_name in extra_table_to_sheet_map:
        test_client.props[table_name] = db[table_name]
    return db
