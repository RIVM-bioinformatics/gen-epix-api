"""Verify organization scope resolution for contact writes."""

from types import SimpleNamespace
from uuid import uuid4

from gen_epix.commondb.domain import command, model
from gen_epix.commondb.policies.is_organization_admin_policy import (
    IsOrganizationAdminPolicy,
)
from gen_epix.fastapp import CrudOperation


def test_contact_scope_resolves_organization_through_site_command() -> None:
    """Resolve contact site IDs to their owning organization IDs."""
    site_id = uuid4()
    organization_id = uuid4()
    site = model.Site(organization_id=organization_id, name="Test site")
    queries: list[command.Command] = []

    def handle(query: command.Command) -> list[model.Site]:
        queries.append(query)
        return [site]

    app = SimpleNamespace(handle=handle)
    policy = object.__new__(IsOrganizationAdminPolicy)
    policy.abac_service = SimpleNamespace(app=app)
    contact = model.Contact(site_id=site_id, name="Test contact")
    contact_command = command.ContactCrudCommand(
        objs=[contact], operation=CrudOperation.UPDATE_SOME
    )

    organization_ids = policy._get_organization_ids_for_contact(contact_command)

    assert organization_ids == {organization_id}
    assert len(queries) == 1
    assert isinstance(queries[0], command.SiteCrudCommand)
    assert queries[0].obj_ids == [site_id]
