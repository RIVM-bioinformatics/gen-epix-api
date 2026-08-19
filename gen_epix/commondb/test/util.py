import logging
from typing import Any

from dynaconf import Dynaconf

from gen_epix.commondb.domain.model import User
from gen_epix.fastapp import App


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


def get_existing_root_user(cfg: dict, app: App) -> User:
    user_manager = app.user_manager
    if user_manager is None:
        raise ValueError("User generator not found")
    root_user_cfg: dict = cfg["service"]["auth"]["props"]["root"]["user"]
    user: User = user_manager.retrieve_user_by_key(  # type: ignore[assignment]
        root_user_cfg["key"]
    )
    return user


def create_root_user_from_claims(cfg: dict | Dynaconf, app: App) -> User:
    user_manager = app.user_manager
    if user_manager is None:
        raise ValueError("User generator not found")
    root_user_cfg: dict = cfg["service"]["auth"]["props"]["root"]["user"]
    user: User = user_manager.create_root_user_from_claims(  # type: ignore[assignment]
        {
            "__key__": root_user_cfg["key"],
            "email": root_user_cfg.get("email"),
            "name": root_user_cfg.get("name"),
        },
    )
    if user.email and not user.name:
        user.name = user.email.split("@")[0]

    return user


def parse_stats(df: list[dict], stats: Any, **kwargs: Any) -> None:
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
