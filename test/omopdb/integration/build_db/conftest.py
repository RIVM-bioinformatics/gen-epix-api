from test.test_client.pytest_hooks import rewrite_parametrized_dependency_markers


def pytest_collection_modifyitems(items):
    rewrite_parametrized_dependency_markers(items)
