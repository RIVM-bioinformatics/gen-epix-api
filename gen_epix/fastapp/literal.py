"""Constants shared by the server and client sides of the framework."""

# Route suffixes of the generated CRUD endpoints. They are defined here, rather
# than only on CrudEndpointGenerator, so that a client can build the same routes
# without importing the endpoint generator and thereby FastAPI.
DEFAULT_BATCH_ROUTE_SUFFIX = "/batch"
DEFAULT_QUERY_ROUTE_SUFFIX = "/query"
DEFAULT_IDS_ROUTE_SUFFIX = "/ids"
DEFAULT_EXISTS_ROUTE_SUFFIX = "/exists"
