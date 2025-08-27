import datetime
import re
import shutil
from enum import Enum
from pathlib import Path
from typing import Hashable

from gen_epix.common.test.enum import RepositoryType


def create_data_fixture(
    repository_cfg: dict,
    services: set[Hashable],
    repository_type: RepositoryType,
    load_target: str,
    test_dir: Path,
) -> None:
    for service_type in services:
        service_type_str = (
            str(service_type.value)
            if isinstance(service_type, Enum)
            else str(service_type)
        )
        curr_cfg = repository_cfg[service_type_str]
        if not curr_cfg:
            # No repository
            continue
        match repository_type:
            case RepositoryType.DICT:
                curr_cfg["file"] = re.sub(
                    r"\.[A-Za-z]+\.pkl\.gz",
                    f".{load_target.lower()}.pkl.gz",
                    curr_cfg["file"],
                    flags=re.IGNORECASE,
                )
            case RepositoryType.SA_SQLITE:
                # Copy sqlite files to test output directory
                source_file = Path(
                    re.sub(
                        r"\.[A-Za-z]+\.sqlite",
                        f".{load_target.lower()}.sqlite",
                        curr_cfg["file"],
                        flags=re.IGNORECASE,
                    )
                )
                if not source_file.is_file():
                    continue
                target_file = test_dir / source_file.name
                curr_cfg["file"] = str(target_file.absolute())
                shutil.copyfile(source_file, target_file)
            case RepositoryType.SA_SQL:
                # Nothing to do
                pass
            case _:
                raise NotImplementedError(
                    f"repository_type {repository_type} not implemented"
                )


def get_test_name(test_type: Enum | str) -> str:
    return (
        datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        + "_"
        + (test_type if isinstance(test_type, str) else test_type.value)
    )


def get_test_root_output_dir() -> Path:
    dir = Path(__file__).parent.parent.parent / "test" / "output"
    dir.mkdir(parents=True, exist_ok=True)
    return dir


def get_test_output_dir(test_name: str) -> Path:
    output_dir = get_test_root_output_dir() / test_name
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir
