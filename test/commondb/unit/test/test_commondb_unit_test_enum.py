from gen_epix.commondb.test.enum import RepositoryType
from gen_epix.commondb.test.enum import TestType as CommondbTestType


def test_test_type_members():
    assert {member.name: member.value for member in CommondbTestType} == {
        "UNIT": "UNIT",
        "INTEGRATION": "INTEGRATION",
        "PERFORMANCE": "PERFORMANCE",
        "OTHER": "OTHER",
        "UNDEFINED": "UNDEFINED",
    }


def test_repository_type_members():
    assert {member.name: member.value for member in RepositoryType} == {
        "DICT": "DICT",
        "SA_SQLITE": "SA_SQLITE",
        "SA_SQL": "SA_SQL",
    }
