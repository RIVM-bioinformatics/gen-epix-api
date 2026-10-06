"""Re-export FastApp API and domain exceptions used by OmopDB."""

# pylint: disable=useless-import-alias
from typing import TYPE_CHECKING

from gen_epix._lazy import LazyExport, lazy_exports
from gen_epix.fastapp.exc import AlreadyExistingIdsError as AlreadyExistingIdsError
from gen_epix.fastapp.exc import AuthException as AuthException
from gen_epix.fastapp.exc import (
    ConcurrentModificationError as ConcurrentModificationError,
)
from gen_epix.fastapp.exc import CredentialsAuthError as CredentialsAuthError
from gen_epix.fastapp.exc import DataException as DataException
from gen_epix.fastapp.exc import DomainException as DomainException
from gen_epix.fastapp.exc import DuplicateIdsError as DuplicateIdsError
from gen_epix.fastapp.exc import (
    FeatureDisabledServiceError as FeatureDisabledServiceError,
)
from gen_epix.fastapp.exc import IdsError as IdsError
from gen_epix.fastapp.exc import (
    InitializationServiceError as InitializationServiceError,
)
from gen_epix.fastapp.exc import InvalidArgumentsError as InvalidArgumentsError
from gen_epix.fastapp.exc import InvalidIdsError as InvalidIdsError
from gen_epix.fastapp.exc import InvalidLinkIdsError as InvalidLinkIdsError
from gen_epix.fastapp.exc import InvalidModelIdsError as InvalidModelIdsError
from gen_epix.fastapp.exc import (
    LinkConstraintViolationError as LinkConstraintViolationError,
)
from gen_epix.fastapp.exc import NoResultsError as NoResultsError
from gen_epix.fastapp.exc import (
    NotNullConstraintViolationError as NotNullConstraintViolationError,
)
from gen_epix.fastapp.exc import (
    RepositoryInitializationServiceError as RepositoryInitializationServiceError,
)
from gen_epix.fastapp.exc import RepositoryServiceError as RepositoryServiceError
from gen_epix.fastapp.exc import (
    RequestLimitExceededAuthError as RequestLimitExceededAuthError,
)
from gen_epix.fastapp.exc import ServiceException as ServiceException
from gen_epix.fastapp.exc import ServiceUnavailableError as ServiceUnavailableError
from gen_epix.fastapp.exc import UnauthorizedAuthError as UnauthorizedAuthError
from gen_epix.fastapp.exc import (
    UniqueConstraintViolationError as UniqueConstraintViolationError,
)
from gen_epix.fastapp.exc import (
    UserAlreadyExistsAuthError as UserAlreadyExistsAuthError,
)
from gen_epix.fastapp.exc import UserNotFoundAuthError as UserNotFoundAuthError

if TYPE_CHECKING:
    from gen_epix.fastapp.api.exc import (
        BadRequest400HTTPException as BadRequest400HTTPException,
    )
    from gen_epix.fastapp.api.exc import (
        Forbidden403HTTPException as Forbidden403HTTPException,
    )
    from gen_epix.fastapp.api.exc import (
        ForeignKeyConstraint409HTTPException as ForeignKeyConstraint409HTTPException,
    )
    from gen_epix.fastapp.api.exc import (
        InternalServerError500HTTPException as InternalServerError500HTTPException,
    )
    from gen_epix.fastapp.api.exc import (
        MethodNotAllowed405HTTPException as MethodNotAllowed405HTTPException,
    )
    from gen_epix.fastapp.api.exc import (
        NotImplemented501HTTPException as NotImplemented501HTTPException,
    )
    from gen_epix.fastapp.api.exc import (
        ResourceConflict409HTTPException as ResourceConflict409HTTPException,
    )
    from gen_epix.fastapp.api.exc import (
        ResourceNotFound404HTTPException as ResourceNotFound404HTTPException,
    )
    from gen_epix.fastapp.api.exc import (
        ServiceUnavailableError503HTTPException as ServiceUnavailableError503HTTPException,
    )
    from gen_epix.fastapp.api.exc import (
        UnauthorizedUser401HTTPException as UnauthorizedUser401HTTPException,
    )
    from gen_epix.fastapp.api.exc import (
        UnprocessableEntity422HTTPException as UnprocessableEntity422HTTPException,
    )

# The HTTP exceptions depend on FastAPI and are resolved on first access, so that
# the domain exceptions can be imported without it
_LAZY_EXPORTS: dict[str, LazyExport] = {
    "BadRequest400HTTPException": (
        "gen_epix.fastapp.api.exc",
        "BadRequest400HTTPException",
    ),
    "UnauthorizedUser401HTTPException": (
        "gen_epix.fastapp.api.exc",
        "UnauthorizedUser401HTTPException",
    ),
    "Forbidden403HTTPException": (
        "gen_epix.fastapp.api.exc",
        "Forbidden403HTTPException",
    ),
    "ResourceNotFound404HTTPException": (
        "gen_epix.fastapp.api.exc",
        "ResourceNotFound404HTTPException",
    ),
    "MethodNotAllowed405HTTPException": (
        "gen_epix.fastapp.api.exc",
        "MethodNotAllowed405HTTPException",
    ),
    "ResourceConflict409HTTPException": (
        "gen_epix.fastapp.api.exc",
        "ResourceConflict409HTTPException",
    ),
    "ForeignKeyConstraint409HTTPException": (
        "gen_epix.fastapp.api.exc",
        "ForeignKeyConstraint409HTTPException",
    ),
    "UnprocessableEntity422HTTPException": (
        "gen_epix.fastapp.api.exc",
        "UnprocessableEntity422HTTPException",
    ),
    "InternalServerError500HTTPException": (
        "gen_epix.fastapp.api.exc",
        "InternalServerError500HTTPException",
    ),
    "NotImplemented501HTTPException": (
        "gen_epix.fastapp.api.exc",
        "NotImplemented501HTTPException",
    ),
    "ServiceUnavailableError503HTTPException": (
        "gen_epix.fastapp.api.exc",
        "ServiceUnavailableError503HTTPException",
    ),
}

if not TYPE_CHECKING:
    # Not visible to type checkers, which would otherwise accept any attribute
    __getattr__, __dir__ = lazy_exports(__name__, _LAZY_EXPORTS)
