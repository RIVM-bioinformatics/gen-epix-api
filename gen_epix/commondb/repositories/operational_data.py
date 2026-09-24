"""Provide failure-safe dictionary clearing for app-specific operational resets."""

from collections.abc import Hashable, Iterable

from gen_epix.fastapp import Model


def delete_dict_operational_data(
    db: dict[type[Model], dict[Hashable, Model]],
    model_classes: Iterable[type[Model]],
) -> None:
    """Clear selected tables in place, restoring them if deletion fails.

    Dictionary units of work do not implement rollback. This operation therefore
    snapshots the selected tables before making changes. Clearing in place keeps
    repository link caches and other repositories' shared table references valid.
    Callers must pause writers for the duration of the reset.

    Args:
        db: Repository tables, keyed by domain model class.
        model_classes: Explicit operational models to clear, children first.

    Raises:
        KeyError: A selected table is missing, before any changes are made.
        BaseException: A table could not be cleared; all selected tables are
            restored before propagation.
    """
    snapshots = [
        (db[model_class], dict(db[model_class])) for model_class in model_classes
    ]
    try:
        for table, _ in snapshots:
            table.clear()
    except BaseException:
        for table, snapshot in snapshots:
            dict.clear(table)
            dict.update(table, snapshot)
        raise
