import datetime
import logging
import os
from enum import Enum
from typing import Any

import pandas as pd

from gen_epix.fastapp import App, User


def get_test_name(test_type: Enum | str) -> str:
    return (
        datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        + "_"
        + (test_type if isinstance(test_type, str) else test_type.value)
    )


def get_test_root_output_dir() -> str:
    dir = os.path.join(os.path.dirname(__file__), "data", "output")
    os.makedirs(dir, exist_ok=True)
    return dir


def get_test_output_dir(test_name: str) -> str:
    output_dir = os.path.join(get_test_root_output_dir(), test_name)
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def set_log_level(
    prefix: str, log_level: int = logging.ERROR, delimiter: str = "."
) -> None:
    def _set_log_level(logger_name: str) -> None:
        logger = logging.getLogger(logger_name)
        logger.setLevel(log_level)
        for handler in logger.handlers:
            handler.setLevel(log_level)

    for suffix in ["setup", "app", "service"]:
        _set_log_level(f"{prefix}{delimiter}{suffix}")
    # Other loggers
    _set_log_level("httpx")


def create_root_user_from_claims(cfg: dict, app: App) -> User:
    user_manager = app.user_manager
    if user_manager is None:
        raise ValueError("User generator not found")
    user = user_manager.create_root_user_from_claims(
        {"email": cfg.secret.root.user.email},
    )
    user.name = user.email.split("@")[0]

    return user


def parse_stats(df: pd.DataFrame, stats: Any, **kwargs: dict) -> None:
    for (
        function_name,
        function_profile,
    ) in stats.get_stats_profile().func_profiles.items():
        row = {**kwargs}
        n_calls = function_profile.ncalls.split("/")
        if len(n_calls) == 1:
            n_calls_min = n_calls[0]
            n_calls_max = n_calls[0]
        else:
            n_calls_min = min(n_calls)
            n_calls_max = max(n_calls)
        row.update(
            {
                "function_name": function_name,
                "n_calls_min": n_calls_min,
                "n_calls_max": n_calls_max,
                "total_time": function_profile.tottime,
                "total_time_per_call": function_profile.percall_tottime,
                "cumulative_time": function_profile.cumtime,
                "cumulative_time_per_call": function_profile.cumtime,
                "file_name": function_profile.file_name,
                "line_number": function_profile.line_number,
            }
        )
        df.append(row)
