import datetime
import secrets
import uuid
from enum import Enum
from pathlib import Path

import pandas as pd


def get_test_name(test_type: Enum | str) -> str:
    return (
        datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d_%H%M%S")
        + "_"
        + (test_type if isinstance(test_type, str) else test_type.value)
    )


def get_test_root_output_dir() -> Path:
    dir = Path(__file__).parent.parent / "output"
    dir.mkdir(parents=True, exist_ok=True)
    return dir


def get_test_output_dir(test_name: str) -> Path:
    output_dir = get_test_root_output_dir() / test_name
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def generate_uuids(n_rows: int = 1000, n_cols: int = 100) -> None:
    df = pd.DataFrame.from_dict(
        {f"uuid{i}": [uuid.uuid4() for j in range(n_rows)] for i in range(n_cols)}
    )
    xls_file = Path(__file__).parent.parent / "output" / "generated_uuids.xlsx"
    df.to_excel(xls_file, sheet_name="uuid", index=False)
    print(
        f"Total of {n_rows} uuids times {df.shape[1]} columns generated and written to file {str(xls_file)}"
    )


def generate_hex_strings(
    n_rows: int = 1000, n_cols: int = 100, length: int = 8
) -> None:
    hex_data = {
        f"hex_string{i}": [f'"{secrets.token_hex(length // 2)}"' for j in range(n_rows)]
        for i in range(n_cols)
    }

    df = pd.DataFrame.from_dict(hex_data)
    xls_file = Path(__file__).parent.parent / "output" / "generated_hex_strings.xlsx"
    df.to_excel(xls_file, sheet_name="hex_string", index=False)
    print(
        f"Total of {n_rows} hex strings times {df.shape[1]} columns generated and written to file {str(xls_file)}"
    )
