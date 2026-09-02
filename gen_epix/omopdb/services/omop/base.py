"""Implementation base that supplies OmopDB runtime metadata to OMOP services."""

from typing import Any

from gen_epix.commondb.app_impl_details import AppImplDetails
from gen_epix.omopdb.domain.service import BaseOmopService as DomainBaseOmopService


class BaseOmopService(DomainBaseOmopService):
    """
    Encapsulates an omopdb service, by providing additional 
    implementation details common to all omopdb services.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the domain service and expose application role mappings."""
        super().__init__(*args, **kwargs)
        app_impl: AppImplDetails = self.app.impl
        self.role_map = app_impl.role_map
        self.role_set_map = app_impl.role_set_map
