import pytest


def rewrite_parametrized_dependency_markers(items: list) -> None:
    """Rewrite class-level dependency 'depends' markers to include parametrize IDs.

    PROBLEM
    -------
    build_db test files declare ordered test classes with static depends strings:

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
    This function runs at collection time, after all items are gathered, and rewrites
    the depends strings for each test item individually so they reference the node
    belonging to the *same* parameter combination as the item being processed:

        TestRead::test_read_user[skip_endpoints__SA_SQLITE_EMPTY]
          → depends on "TestCreate::test_create_user_first_root[skip_endpoints__SA_SQLITE_EMPTY]"

        TestRead::test_read_user[skip_endpoints__DICT_EMPTY]
          → depends on "TestCreate::test_create_user_first_root[skip_endpoints__DICT_EMPTY]"

        TestRead::test_read_user[with_endpoints__DICT_EMPTY]
          → depends on "TestCreate::test_create_user_first_root[with_endpoints__DICT_EMPTY]"

    Each combination therefore forms its own isolated Create→Read→Update→Delete chain.
    A failure in one combination skips only that combination's downstream tests;
    the other combinations are unaffected.
    """
    # First pass: find every class whose pytestmark contains a `dependency` marker
    # with a `depends=` argument AND whose items are parametrized (have a callspec).
    # Strip that marker from the class so it won't be evaluated as a static
    # class-level dependency; we replace it below with per-item markers.
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

    # Second pass: attach a new dependency marker to each item with the depends
    # string rewritten to include the item's own parameter ID.
    for item in items:
        cls = getattr(item, "cls", None)
        if cls not in class_dep_marks:
            continue
        dep_marks = class_dep_marks[cls]
        if not hasattr(item, "callspec"):
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
