import pickle

from gen_epix.casedb.domain.model.case import case_data, ops_data


def test_legacy_case_data_pickle_module_resolves_to_operational_models() -> None:
    """Load a class reference emitted before case_data was renamed."""
    legacy_case_pickle = (
        b"cgen_epix.casedb.domain.model.case.case_data\n" b"Case\n" b"."
    )

    assert pickle.loads(legacy_case_pickle) is ops_data.Case
    assert case_data.Case is ops_data.Case
