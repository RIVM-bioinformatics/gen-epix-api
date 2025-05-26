# pylint: disable=too-few-public-methods
# This module defines base classes, methods are added later


from typing import ClassVar

import gen_epix.casedb.domain.model.case.case
from gen_epix.casedb.domain import DOMAIN, model
from gen_epix.casedb.domain.command.base import CrudCommand
from gen_epix.fastapp import PermissionTypeSet


# geo
class RegionSetCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.RegionSet


class RegionCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.Region


class RegionRelationCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.RegionRelation


class RegionSetShapeCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.RegionSetShape


# ontology
class ConceptCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.Concept


class ConceptSetCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.ConceptSet


class ConceptSetMemberCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.ConceptSetMember


class DiseaseCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.Disease


class EtiologicalAgentCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.EtiologicalAgent


class EtiologyCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.Etiology


# organization
class OrganizationCrudCommand(CrudCommand):
    PERMISSION_TYPE_SET: ClassVar = PermissionTypeSet.CRU
    MODEL_CLASS: ClassVar = model.Organization


class UserCrudCommand(CrudCommand):
    PERMISSION_TYPE_SET: ClassVar = PermissionTypeSet.CRU
    MODEL_CLASS: ClassVar = model.User


class OrganizationSetCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.OrganizationSet


class OrganizationSetMemberCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.OrganizationSetMember


class SiteCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.Site


class ContactCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.Contact


class IdentifierIssuerCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.IdentifierIssuer


class DataCollectionCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.DataCollection


class DataCollectionSetCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.DataCollectionSet


class DataCollectionSetMemberCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.DataCollectionSetMember


class DataCollectionRelationCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.DataCollectionRelation


# rbac
class UserInvitationCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.UserInvitation


# subject
class SubjectCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.Subject


class SubjectIdentifierCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.SubjectIdentifier


# case
class TreeAlgorithmClassCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = gen_epix.casedb.domain.model.case.case.TreeAlgorithmClass


class TreeAlgorithmCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = gen_epix.casedb.domain.model.case.case.TreeAlgorithm


class GeneticDistanceProtocolCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = (
        gen_epix.casedb.domain.model.case.case.GeneticDistanceProtocol
    )


class CaseTypeCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.CaseType


class CaseTypeSetCategoryCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.CaseTypeSetCategory


class CaseTypeSetCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.CaseTypeSet


class CaseTypeSetMemberCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.CaseTypeSetMember


class DimCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.Dim


class ColCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.Col


class CaseTypeColSetCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.CaseTypeColSet


class CaseTypeColSetMemberCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.CaseTypeColSetMember


class CaseTypeColCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.CaseTypeCol


class CaseCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.Case


class CaseDataCollectionLinkCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.CaseDataCollectionLink


class CaseSetCategoryCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.CaseSetCategory


class CaseSetStatusCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.CaseSetStatus


class CaseSetCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.CaseSet


class CaseSetMemberCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.CaseSetMember


class CaseSetDataCollectionLinkCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.CaseSetDataCollectionLink


# abac
class OrganizationAdminPolicyCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.OrganizationAdminPolicy


class OrganizationAccessCasePolicyCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.OrganizationAccessCasePolicy


class UserAccessCasePolicyCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.UserAccessCasePolicy


class OrganizationShareCasePolicyCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.OrganizationShareCasePolicy


class UserShareCasePolicyCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.UserShareCasePolicy


# system
class OutageCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.Outage


DOMAIN.register_locals(locals())
