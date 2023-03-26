from bootstrap.introspection import edit_source_code, get_source_code


def test_get_source_code():
    function_code = get_source_code("bootstrap.dummy_module.dummy_function")
    assert function_code is not None
    assert "def dummy_function(a, b):" in function_code

    class_code = get_source_code("bootstrap.dummy_module.DummyClass")
    assert class_code is not None
    assert "class DummyClass:" in class_code


def test_edit_source_code():
    original_code = get_source_code("bootstrap.dummy_module.dummy_function")
    new_code = "def dummy_function(a, b):\n    return a + b"
    assert edit_source_code("bootstrap.dummy_module.dummy_function", new_code)

    edited_code = get_source_code("bootstrap.dummy_module.dummy_function")
    assert edited_code == new_code

    # Revert the code back to the original version
    assert edit_source_code("bootstrap.dummy_module.dummy_function", original_code)

    reverted_code = get_source_code("bootstrap.dummy_module.dummy_function")
    assert reverted_code == original_code
