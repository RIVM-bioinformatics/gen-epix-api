import pytest


def pytest_collection_modifyitems(items):
    """Rewrite class-level dependency 'depends' markers to include parametrize IDs.

    PROBLEM
    -------
    test_casedb_build.py declares ordered test classes with static depends strings:

        @pytest.mark.dependency(depends=["TestCreate::test_create_user_first_root"])
        class TestRead(ModuleTestRead):
            pass

    But the `env` fixture is parametrized with three combinations. pytest therefore
    generates one node per (test, combination) pair, appending the combination ID
    in brackets:

        TestCreate::test_create_user_first_root[skip_endpoints__SA_SQLITE_EMPTY]
        TestCreate::test_create_user_first_root[skip_endpoints__DICT_EMPTY]
        TestCreate::test_create_user_first_root[with_endpoints__DICT_EMPTY]

    pytest-dependency resolves dependencies by exact node ID. The static string
    "TestCreate::test_create_user_first_root" never matches any of the suffixed IDs,
    so without this hook all TestRead/TestUpdate/TestDelete tests would be
    unconditionally skipped for every combination.

    SOLUTION
    --------
    This hook runs at collection time, after all items are gathered, and rewrites
    the depends strings for each test item individually so they reference the node
    belonging to the *same* parameter combination as the item being processed:

        TestRead::test_read_user[skip_endpoints__SA_SQLITE_EMPTY]
          → depends on "TestCreate::test_create_user_first_root[skip_endpoints__SA_SQLITE_EMPTY]"

        TestRead::test_read_user[skip_endpoints__DICT_EMPTY]
          → depends on "TestCreate::test_create_user_first_root[skip_endpoints__DICT_EMPTY]"

        TestRead::test_read_user[with_endpoints__DICT_EMPTY]
          → depends on "TestCreate::test_create_user_first_root[with_endpoints__DICT_EMPTY]"

    Each combination therefore forms its own isolated Create→Read→Update→Delete chain.
    A failure in the SA_SQLITE_EMPTY combination skips only that combination's
    downstream tests; the DICT_EMPTY combinations are unaffected.
    """
    # -------------------------------------------------------------------------
    # First pass: find every class whose pytestmark contains a `dependency`
    # marker with a `depends=` argument AND whose items are parametrized
    # (i.e. have a callspec). Strip that marker from the class so it won't be
    # evaluated as a static class-level dependency by pytest-dependency; we will
    # replace it below with per-item markers that carry the correct suffixed IDs.
    #
    # Example state after this pass for TestRead:
    #   class_dep_marks[TestRead] = [Mark("dependency", depends=["TestCreate::test_create_user_first_root"])]
    #   TestRead.pytestmark  = [<other marks, e.g. scenario_ids>]  # depends mark removed
    # -------------------------------------------------------------------------
    class_dep_marks: dict = {}
    for item in items:
        cls = getattr(item, "cls", None)
        if cls is None or cls in class_dep_marks:
            continue
        cls_marks = getattr(cls, "pytestmark", [])
        dep_marks = [
            m for m in cls_marks if m.name == "dependency" and m.kwargs.get("depends")
        ]
        if not dep_marks:
            continue
        class_items = [i for i in items if getattr(i, "cls", None) is cls]
        if any(hasattr(i, "callspec") for i in class_items):
            class_dep_marks[cls] = dep_marks
            cls.pytestmark = [
                m
                for m in cls_marks
                if not (m.name == "dependency" and m.kwargs.get("depends"))
            ]

    if not class_dep_marks:
        return

    # -------------------------------------------------------------------------
    # Second pass: for every item whose class was harvested above, attach a new
    # dependency marker with the depends string rewritten to include the item's
    # own parameter ID.
    #
    # callspec.id is the human-readable combination string, e.g.:
    #   "skip_endpoints__SA_SQLITE_EMPTY"
    #
    # Example transformation for item
    #   TestRead::test_read_user[skip_endpoints__SA_SQLITE_EMPTY]:
    #
    #   original depends entry : "TestCreate::test_create_user_first_root"
    #   param_id               : "skip_endpoints__SA_SQLITE_EMPTY"
    #   rewritten depends entry: "TestCreate::test_create_user_first_root[skip_endpoints__SA_SQLITE_EMPTY]"
    #
    # The `if "[" not in d` guard avoids double-suffixing entries that were
    # already written with an explicit bracket (e.g. hand-crafted cross-param
    # dependencies), leaving them unchanged.
    #
    # Non-parametrized items (no callspec) keep the original marker unchanged
    # because their node ID has no suffix and an exact match is possible.
    # -------------------------------------------------------------------------
    for item in items:
        cls = getattr(item, "cls", None)
        if cls not in class_dep_marks:
            continue
        dep_marks = class_dep_marks[cls]
        if not hasattr(item, "callspec"):
            # No parameter suffix → use the static marker as-is.
            for dep_mark in dep_marks:
                item.add_marker(dep_mark, append=True)
        else:
            param_id = item.callspec.id
            for dep_mark in dep_marks:
                new_depends = [
                    f"{d}[{param_id}]" if "[" not in d else d
                    for d in dep_mark.kwargs["depends"]
                ]
                new_kwargs = {**dep_mark.kwargs, "depends": new_depends}
                item.add_marker(pytest.mark.dependency(**new_kwargs), append=True)
