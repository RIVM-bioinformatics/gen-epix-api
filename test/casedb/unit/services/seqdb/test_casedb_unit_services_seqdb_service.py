"""Unit tests for casedb's seqdb service composition."""

from test.util.mock_compat import Mock, patch

import pytest

from gen_epix.casedb.services.seqdb import service
from gen_epix.casedb.services.seqdb.service import SeqdbService
from gen_epix.fastapp import exc


def test_lowercase_client_type_is_rejected() -> None:
    """Reject lowercase setup values before constructing dependencies."""
    with pytest.raises(exc.InitializationServiceError, match="in uppercase"):
        SeqdbService(Mock(), "none")


def test_none_client_type_uses_no_app_composer() -> None:
    """Use the exception-raising composer for the NONE setup mode."""
    with (
        patch.object(service.BaseSeqdbService, "__init__", return_value=None),
        patch.object(
            service.SeqdbClient,
            "create_local_or_remote",
            return_value=(Mock(), None),
        ) as create_client,
    ):
        SeqdbService(Mock(), "NONE")

    assert (
        create_client.call_args.kwargs["app_composer_class"]
        is service.SeqdbNoAppComposer
    )
