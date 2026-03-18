from dataclasses import dataclass

from gen_epix.commondb.domain import enum as commondb_enum


@dataclass
class BuildDbParams:
    skip_endpoints: bool
    dev_repository_config: commondb_enum.DevRepositoryConfig

    @property
    def id(self) -> str:
        prefix = "skip_endpoints" if self.skip_endpoints else "with_endpoints"
        return f"{prefix}__{self.dev_repository_config.value}"
