import pytest

import gen_epix.commondb.domain.exc as commondb_exc
import gen_epix.fastapp.api.exc as fastapp_api_exc
import gen_epix.fastapp.exc as fastapp_exc


@pytest.mark.parametrize(
    "name,source_module",
    [
        pytest.param("DomainException", fastapp_exc, id="domain-exception"),
        pytest.param("ServiceException", fastapp_exc, id="service-exception"),
        pytest.param(
            "InitializationServiceError",
            fastapp_exc,
            id="initialization-service-error",
        ),
        pytest.param("CredentialsAuthError", fastapp_exc, id="credentials-auth-error"),
        pytest.param(
            "UnauthorizedAuthError", fastapp_exc, id="unauthorized-auth-error"
        ),
        pytest.param(
            "BadRequest400HTTPException",
            fastapp_api_exc,
            id="bad-request-http-exception",
        ),
        pytest.param(
            "Forbidden403HTTPException",
            fastapp_api_exc,
            id="forbidden-http-exception",
        ),
        pytest.param(
            "ResourceNotFound404HTTPException",
            fastapp_api_exc,
            id="not-found-http-exception",
        ),
    ],
)
def test_reexports_fastapp_exception_types(name: str, source_module: object) -> None:
    """Expose shared FastApp exception types through the commondb facade."""
    assert getattr(commondb_exc, name) is getattr(source_module, name)
