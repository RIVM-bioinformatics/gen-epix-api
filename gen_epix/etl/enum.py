from enum import Enum


class EtlStatus(Enum):
    """Encapsulates lifecycle outcomes for ETL and upload processing."""

    PENDING = "PENDING"  # Yet to be processed
    SKIPPED = "SKIPPED"  # No changes stored
    FAILED = "FAILED"
    CREATED = "CREATED"
    UPDATED = "UPDATED"
    DELETED = "DELETED"
    MIXED = "MIXED"  # TODO: should likely be merged with PROCESSED, or at least clarify the distinction
    PROCESSED = "PROCESSED"  # Skipped, created or updated (not failed)
    SUCCESS = "SUCCESS"


class EtlStatusSet(Enum):
    """Encapsulates grouping of ETL statuses by failure and processing outcome."""

    NOT_FAILED = frozenset(
        {
            EtlStatus.PENDING,
            EtlStatus.SKIPPED,
            EtlStatus.CREATED,
            EtlStatus.UPDATED,
            EtlStatus.DELETED,
            EtlStatus.PROCESSED,
            EtlStatus.SUCCESS,
        }
    )
    FAILED = frozenset({EtlStatus.FAILED})
    SUCCEEDED = frozenset(
        {
            EtlStatus.SKIPPED,
            EtlStatus.CREATED,
            EtlStatus.UPDATED,
            EtlStatus.DELETED,
            EtlStatus.PROCESSED,
            EtlStatus.SUCCESS,
        }
    )
    COMPOUND = frozenset(
        {
            EtlStatus.PENDING,
            EtlStatus.FAILED,
            EtlStatus.SUCCESS,
        }
    )
