from re import Match, Pattern, compile
from salve_ipc.server_functions import get_definition


def test_get_definition():
    python_regexes: list[tuple[str, str]] = [
        (r"def ", "after"),
        (r"import .*,? ", "after"),
        (r"from ", "after"),
        (r"class ", "after"),
        (r":?.*=.*", "ahead"),
    ]
    file = open("tests/testing_file2.py").read()

    assert get_definition(
        file,
        python_regexes,
        "test",
    ) == (11, 6, 4)

    assert get_definition(
        file,
        python_regexes,
        "example",
    ) == (3, 0, 7)

    assert get_definition(
        file,
        python_regexes,
        "re",
    ) == (1, 5, 2)

    assert get_definition(
        file,
        python_regexes,
        "x",
    ) == (5, 3, 1)

    assert get_definition(
        file,
        [("", "ahead")],
        "x",
    ) == (5, 3, 1)

    assert get_definition(
        file,
        [("", "ahead")],
        "test",
    ) == (8, 0, 4)
