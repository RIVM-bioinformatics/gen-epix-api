"""Public API routing types for FastApp applications.

The package exposes ``CrudEndpointGenerator`` for adding command-backed CRUD
routes, ``CrudEndpointSet`` for configuring a resource's API models and route
behavior, and ``RouterData`` for registering router factory functions during
application composition.
"""

# pylint: disable=useless-import-alias
from gen_epix.fastapp.api.crud_endpoint_generator import (
    CrudEndpointGenerator as CrudEndpointGenerator,
)
from gen_epix.fastapp.api.crud_endpoint_set import CrudEndpointSet as CrudEndpointSet
from gen_epix.fastapp.api.router import RouterData as RouterData
