"""Define SQLAlchemy rows and mixins for commondb system persistence."""

import datetime
from uuid import UUID

import sqlalchemy.orm as orm
from sqlalchemy.orm import Mapped, declarative_mixin

from gen_epix.commondb.domain import DOMAIN, enum, model
from gen_epix.commondb.repositories.sa_model.base import RowMetadataMixin
from gen_epix.commondb.repositories.sa_model.util import (
    create_mapped_column,
    create_table_args,
)

Base: type = orm.declarative_base(name=enum.ServiceType.SYSTEM.value)


@declarative_mixin
class OutageMixin(RowMetadataMixin):
    """Encapsulates SQLAlchemy columns for Outage-derived row models.

    The mixin supports derived domain models whose SQLAlchemy models are
    created under a different declarative base.
    """

    description: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.Outage, "description"
    )
    active_from: Mapped[datetime.datetime | None] = create_mapped_column(
        DOMAIN, model.Outage, "active_from"
    )
    active_to: Mapped[datetime.datetime | None] = create_mapped_column(
        DOMAIN, model.Outage, "active_to"
    )
    visible_from: Mapped[datetime.datetime | None] = create_mapped_column(
        DOMAIN, model.Outage, "visible_from"
    )
    visible_to: Mapped[datetime.datetime | None] = create_mapped_column(
        DOMAIN, model.Outage, "visible_to"
    )
    is_active: Mapped[bool | None] = create_mapped_column(
        DOMAIN, model.Outage, "is_active"
    )
    is_visible: Mapped[bool | None] = create_mapped_column(
        DOMAIN, model.Outage, "is_visible"
    )


class Outage(Base, OutageMixin):
    """Encapsulates persistence of the commondb Outage domain model."""

    __tablename__, __table_args__ = create_table_args(model.Outage)


@declarative_mixin
class UploadJobMixin(RowMetadataMixin):
    """Encapsulates SQLAlchemy columns for UploadJob-derived row models."""

    user_id: Mapped[UUID] = create_mapped_column(DOMAIN, model.UploadJob, "user_id")
    job_type: Mapped[str] = create_mapped_column(DOMAIN, model.UploadJob, "job_type")
    status: Mapped[enum.UploadJobStatus] = create_mapped_column(
        DOMAIN, model.UploadJob, "status"
    )
    submitted_at: Mapped[datetime.datetime] = create_mapped_column(
        DOMAIN, model.UploadJob, "submitted_at"
    )
    started_at: Mapped[datetime.datetime | None] = create_mapped_column(
        DOMAIN, model.UploadJob, "started_at"
    )
    finished_at: Mapped[datetime.datetime | None] = create_mapped_column(
        DOMAIN, model.UploadJob, "finished_at"
    )
    heartbeat_at: Mapped[datetime.datetime | None] = create_mapped_column(
        DOMAIN, model.UploadJob, "heartbeat_at"
    )
    worker_id: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.UploadJob, "worker_id"
    )
    result_json: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.UploadJob, "result_json"
    )
    error_status_code: Mapped[int | None] = create_mapped_column(
        DOMAIN, model.UploadJob, "error_status_code"
    )
    error_detail: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.UploadJob, "error_detail"
    )


class UploadJob(Base, UploadJobMixin):
    """Encapsulates persistence of the commondb UploadJob domain model."""

    __tablename__, __table_args__ = create_table_args(model.UploadJob)
