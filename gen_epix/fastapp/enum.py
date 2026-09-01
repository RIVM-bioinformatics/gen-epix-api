"""Enumerations shared by the application framework."""

from enum import Enum


class SortOrder(Enum):
    """Specify ascending or descending ordering."""

    ASCENDING = "ASCENDING"
    DESCENDING = "DESCENDING"


class PermissionType(Enum):
    """Specify the action authorized by a permission."""

    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    EXECUTE = "EXECUTE"


class PermissionTypeSet(Enum):
    """Provide named combinations of permission types."""

    E = frozenset({PermissionType.EXECUTE})
    CRUD = frozenset(
        {
            PermissionType.CREATE,
            PermissionType.READ,
            PermissionType.UPDATE,
            PermissionType.DELETE,
        }
    )
    CRU = frozenset(
        {
            PermissionType.CREATE,
            PermissionType.READ,
            PermissionType.UPDATE,
        }
    )  # Undeletable
    CRD = frozenset(
        {
            PermissionType.CREATE,
            PermissionType.READ,
            PermissionType.DELETE,
        }
    )  # Immutable and deletable
    CUD = frozenset(
        {
            PermissionType.CREATE,
            PermissionType.UPDATE,
            PermissionType.DELETE,
        }
    )
    RUD = frozenset(
        {
            PermissionType.READ,
            PermissionType.UPDATE,
            PermissionType.DELETE,
        }
    )
    CR = frozenset({PermissionType.CREATE, PermissionType.READ})  # Immutable
    CU = frozenset({PermissionType.CREATE, PermissionType.UPDATE})
    CD = frozenset({PermissionType.CREATE, PermissionType.DELETE})
    RU = frozenset({PermissionType.READ, PermissionType.UPDATE})
    RD = frozenset({PermissionType.READ, PermissionType.DELETE})
    UD = frozenset({PermissionType.UPDATE, PermissionType.DELETE})
    C = frozenset({PermissionType.CREATE})
    R = frozenset({PermissionType.READ})  # Read only
    U = frozenset({PermissionType.UPDATE})
    D = frozenset({PermissionType.DELETE})
    NONE = frozenset()


class CrudOperation(Enum):
    """Identify a supported create, read, update, delete, or existence operation."""

    CREATE_ONE = "CREATE_ONE"
    CREATE_SOME = "CREATE_SOME"
    READ_ALL = "READ_ALL"
    READ_SOME = "READ_SOME"
    READ_ONE = "READ_ONE"
    UPDATE_ONE = "UPDATE_ONE"
    UPDATE_SOME = "UPDATE_SOME"
    UPSERT_ONE = "UPSERT_ONE"
    UPSERT_SOME = "UPSERT_SOME"
    DELETE_ONE = "DELETE_ONE"
    DELETE_SOME = "DELETE_SOME"
    DELETE_ALL = "DELETE_ALL"
    UNDELETE_ONE = "UNDELETE_ONE"
    UNDELETE_SOME = "UNDELETE_SOME"
    UNDELETE_ALL = "UNDELETE_ALL"
    EXISTS_ONE = "EXISTS_ONE"
    EXISTS_SOME = "EXISTS_SOME"


class CrudOperationSet(Enum):
    """Provide named combinations of CRUD operations."""

    CREATE = frozenset({CrudOperation.CREATE_ONE, CrudOperation.CREATE_SOME})
    READ = frozenset(
        {
            CrudOperation.READ_ALL,
            CrudOperation.READ_SOME,
            CrudOperation.READ_ONE,
        }
    )
    READ_NOT_ALL = frozenset(
        {
            CrudOperation.READ_SOME,
            CrudOperation.READ_ONE,
        }
    )
    UPDATE = frozenset({CrudOperation.UPDATE_ONE, CrudOperation.UPDATE_SOME})
    DELETE = frozenset(
        {
            CrudOperation.DELETE_ONE,
            CrudOperation.DELETE_SOME,
            CrudOperation.DELETE_ALL,
        }
    )
    EXISTS = frozenset({CrudOperation.EXISTS_ONE, CrudOperation.EXISTS_SOME})
    WRITE = frozenset(
        {
            CrudOperation.CREATE_ONE,
            CrudOperation.CREATE_SOME,
            CrudOperation.UPDATE_ONE,
            CrudOperation.UPDATE_SOME,
            CrudOperation.UPSERT_ONE,
            CrudOperation.UPSERT_SOME,
        }
    )
    WRITE_OR_READ_ALL_OR_DELETE_ALL = frozenset(
        {
            CrudOperation.CREATE_ONE,
            CrudOperation.CREATE_SOME,
            CrudOperation.UPDATE_ONE,
            CrudOperation.UPDATE_SOME,
            CrudOperation.UPSERT_ONE,
            CrudOperation.UPSERT_SOME,
            CrudOperation.READ_ALL,
            CrudOperation.DELETE_ALL,
        }
    )
    READ_OR_EXISTS = frozenset(
        {
            CrudOperation.READ_ALL,
            CrudOperation.READ_SOME,
            CrudOperation.READ_ONE,
            CrudOperation.EXISTS_ONE,
            CrudOperation.EXISTS_SOME,
        }
    )
    NON_READ = frozenset(
        {
            CrudOperation.CREATE_ONE,
            CrudOperation.CREATE_SOME,
            CrudOperation.EXISTS_ONE,
            CrudOperation.EXISTS_SOME,
            CrudOperation.UPDATE_ONE,
            CrudOperation.UPDATE_SOME,
            CrudOperation.UPSERT_ONE,
            CrudOperation.UPSERT_SOME,
            CrudOperation.DELETE_ONE,
            CrudOperation.DELETE_SOME,
            CrudOperation.DELETE_ALL,
        }
    )
    NON_READ_OR_EXISTS = frozenset(
        {
            CrudOperation.CREATE_ONE,
            CrudOperation.CREATE_SOME,
            CrudOperation.UPDATE_ONE,
            CrudOperation.UPDATE_SOME,
            CrudOperation.UPSERT_ONE,
            CrudOperation.UPSERT_SOME,
            CrudOperation.DELETE_ONE,
            CrudOperation.DELETE_SOME,
            CrudOperation.DELETE_ALL,
        }
    )
    UNDELETE = frozenset(
        {
            CrudOperation.UNDELETE_ONE,
            CrudOperation.UNDELETE_SOME,
            CrudOperation.UNDELETE_ALL,
        }
    )
    WRITE_ONE = frozenset(
        {
            CrudOperation.CREATE_ONE,
            CrudOperation.UPDATE_ONE,
            CrudOperation.UPSERT_ONE,
        }
    )
    WRITE_SOME = frozenset(
        {
            CrudOperation.CREATE_SOME,
            CrudOperation.UPDATE_SOME,
            CrudOperation.UPSERT_SOME,
        }
    )
    NON_CREATE_ONE = frozenset(
        {
            CrudOperation.READ_ONE,
            CrudOperation.UPDATE_ONE,
            CrudOperation.DELETE_ONE,
            CrudOperation.EXISTS_ONE,
        }
    )
    NON_CREATE_SOME = frozenset(
        {
            CrudOperation.READ_SOME,
            CrudOperation.UPDATE_SOME,
            CrudOperation.DELETE_SOME,
            CrudOperation.EXISTS_SOME,
        }
    )
    ANY_ONE = frozenset(
        {
            CrudOperation.CREATE_ONE,
            CrudOperation.READ_ONE,
            CrudOperation.UPDATE_ONE,
            CrudOperation.DELETE_ONE,
            CrudOperation.EXISTS_ONE,
        }
    )
    ANY_ALL = frozenset(
        {
            CrudOperation.READ_ALL,
            CrudOperation.DELETE_ALL,
        }
    )


class HttpProtocol(Enum):
    """Specify an HTTP transport protocol."""

    HTTP = "HTTP"
    HTTPS = "HTTPS"


class CrudEndpointType(Enum):
    """Identify a generated CRUD endpoint shape."""

    POST_ONE = "POST_ONE"
    POST_SOME = "POST_SOME"
    GET_ALL = "GET_ALL"
    GET_SOME = "GET_SOME"
    GET_ONE = "GET_ONE"
    PUT_ONE = "PUT_ONE"
    PUT_SOME = "PUT_SOME"
    DELETE_ONE = "DELETE_ONE"
    DELETE_SOME = "DELETE_SOME"
    DELETE_ALL = "DELETE_ALL"
    POST_QUERY = "POST_QUERY"
    POST_QUERY_IDS = "POST_QUERY_IDS"


class IsolationLevel(Enum):
    """Specify the transaction isolation level for a database session."""

    READ_UNCOMMITED = "READ_UNCOMMITED"
    READ_COMMITED = "READ_COMMITED"
    REPEATABLE_READ = "REPEATABLE_READ"
    SERIALIZABLE = "SERIALIZABLE"


class LogLevel(Enum):
    """Specify a supported logging severity."""

    FATAL = "FATAL"
    ERROR = "ERROR"
    WARN = "WARN"
    INFO = "INFO"
    DEBUG = "DEBUG"
    TRACE = "TRACE"


class LogLevelSet(Enum):
    """Provide named combinations of logging severities."""

    ERROR_OR_WORSE = frozenset({LogLevel.ERROR, LogLevel.FATAL})
    WARN_OR_WORSE = frozenset({LogLevel.WARN, LogLevel.ERROR, LogLevel.FATAL})
    INFO_OR_WORSE = frozenset(
        {LogLevel.INFO, LogLevel.WARN, LogLevel.ERROR, LogLevel.FATAL}
    )
    DEBUG_OR_WORSE = frozenset(
        {LogLevel.DEBUG, LogLevel.INFO, LogLevel.WARN, LogLevel.ERROR, LogLevel.FATAL}
    )
    TRACE_OR_WORSE = frozenset(
        {
            LogLevel.TRACE,
            LogLevel.DEBUG,
            LogLevel.INFO,
            LogLevel.WARN,
            LogLevel.ERROR,
            LogLevel.FATAL,
        }
    )


class EventTiming(Enum):
    """Identify a phase in command execution."""

    BEFORE = "BEFORE"
    DURING = "DURING"
    AFTER = "AFTER"


class AuthProtocol(Enum):
    """Identify an authentication protocol supported by an identity provider."""

    NONE = "NONE"
    OAUTH2 = "OAUTH2"
    OIDC = "OIDC"


class OAuthFlow(Enum):
    """Identify an OAuth authorization flow."""

    AUTHORIZATION_CODE = "AUTHORIZATION_CODE"
    CLIENT_CREDENTIALS = "CLIENT_CREDENTIALS"
    RESOURCE_OWNER = "RESOURCE_OWNER"
    HYBRID = "HYBRID"
    DEVICE_AUTHORIZATION = "DEVICE_AUTHORIZATION"
    PKCE = "PKCE"


class HttpMethod(Enum):
    """Identify an HTTP request method."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    CONNECT = "CONNECT"
    OPTIONS = "OPTIONS"
    TRACE = "TRACE"


class StringCasing(Enum):
    """Identify a string naming convention."""

    SNAKE_CASE = "SNAKE_CASE"
    CAMEL_CASE = "CAMEL_CASE"
    PASCAL_CASE = "PASCAL_CASE"
    KEBAB_CASE = "KEBAB_CASE"


class FieldType(Enum):
    """
    This enumeration is used to categorize the different types of fields that can be
    present in a model as well as in its persisted version.

    Attributes:
    ----------
    ID : Enum
        Represents an identifier field in the model.
    LINK : Enum
        Represents a link field in the model.
    VALUE : Enum
        Represents a value field in the model.
    RELATIONSHIP : Enum
        Represents a relationship (back-populate) field in the model.
    SERVICE_METADATA : Enum
        Represents a metadata field generated by the service.
    DB_METADATA : Enum
        Represents a metadata field generated by the repository.
    """

    ID = "ID"
    LINK = "LINK"
    VALUE = "VALUE"
    COMPUTED = "COMPUTED"
    RELATIONSHIP = "RELATIONSHIP"
    SERVICE_METADATA = "SERVICE_METADATA"
    DB_METADATA = "DB_METADATA"


class FieldTypeSet(Enum):
    """
    Different sets of field types that can be used to categorize the fields in a model.

    The value is a tuple instead of a frozenset to guarantee the order of the elements.
    """

    ID = tuple([FieldType.ID])
    LINK = tuple([FieldType.LINK])
    VALUE = tuple([FieldType.VALUE])
    RELATIONSHIP = tuple([FieldType.RELATIONSHIP])
    COMPUTED = tuple([FieldType.COMPUTED])
    SERVICE_METADATA = tuple([FieldType.SERVICE_METADATA])
    DB_METADATA = tuple([FieldType.DB_METADATA])
    DATA = tuple([FieldType.LINK, FieldType.VALUE])
    METADATA = tuple([FieldType.SERVICE_METADATA, FieldType.DB_METADATA])
    MODEL_DB_COMMON = tuple([FieldType.ID, FieldType.LINK, FieldType.VALUE])
    MODEL = tuple(
        [
            FieldType.ID,
            FieldType.LINK,
            FieldType.VALUE,
            FieldType.RELATIONSHIP,
            FieldType.COMPUTED,
        ]
    )
    MODEL_ONLY = tuple([FieldType.RELATIONSHIP, FieldType.COMPUTED])
    DB_MODEL_ONLY = tuple([FieldType.SERVICE_METADATA, FieldType.DB_METADATA])
    DB_MODEL = tuple(
        [
            FieldType.ID,
            FieldType.LINK,
            FieldType.VALUE,
            FieldType.SERVICE_METADATA,
            FieldType.DB_METADATA,
        ]
    )


class OnException(Enum):
    """Specify how command execution responds to an exception."""

    RAISE = "RAISE"
    IGNORE = "IGNORE"
    SKIP = "SKIP"
    REPLACE = "REPLACE"
    SET_DEFAULT = "SET_DEFAULT"
    SET_NONE = "SET_NONE"
    SET_NO_RETURN = "SET_NO_RETURN"


class FileExtension(Enum):
    """Identify a supported file extension."""

    PKL = ".pkl"
    JSON = ".json"
    ZIP = ".zip"
