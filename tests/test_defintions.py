from salve_ipc.server_functions import get_definition


def test_get_definition():
    python_regexes: list[tuple[str, str]] = [
        (r"def ", "after"),
        (r"import .*,? ", "after"),
        (r"from ", "after"),
        (r"class ", "after"),
        (r":?.*=.*", "before"),
    ]
    file = open("tests/testing_file2.py", "r+").read()

    assert get_definition(
        file,
        python_regexes,
        "test",
    ) == ((11, 6), 4, "Definition")

    assert get_definition(
        file,
        python_regexes,
        "example",
    ) == ((3, 0), 7, "Definition")

    assert get_definition(
        file,
        python_regexes,
        "re",
    ) == ((1, 5), 2, "Definition")

    assert get_definition(
        file,
        python_regexes,
        "x",
    ) == ((5, 3), 1, "Definition")

    assert get_definition(
        file,
        [("", "before")],
        "x",
    ) == ((5, 3), 1, "Definition")

    assert get_definition(
        file,
        [("", "before")],
        "test",
    ) == ((8, 0), 4, "Definition")
