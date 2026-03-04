def test_pytest_collection_configuration(pytestconfig) -> None:
    assert pytestconfig.getini("testpaths") == ["tests"]
    assert pytestconfig.getini("python_files") == ["test_*.py"]
    assert pytestconfig.getini("python_classes") == ["Test*"]
    assert pytestconfig.getini("python_functions") == ["test_*"]
