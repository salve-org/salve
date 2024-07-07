from time import sleep

from salve_ipc import (
    AUTOCOMPLETE,
    DEFINITION,
    EDITORCONFIG,
    HIGHLIGHT,
    IPC,
    REPLACEMENTS,
    Response,
)


def test_IPC():
    context = IPC()

    context.update_file("test", open("tests/testing_file1.py", "r+").read())

    context.request(
        AUTOCOMPLETE,
        file="test",
        expected_keywords=[],
        current_word="t",
    )
    context.request(
        REPLACEMENTS,
        file="test",
        expected_keywords=[],
        current_word="thid",
    )
    context.request(HIGHLIGHT, file="test", language="python")
    context.request(EDITORCONFIG, file_path=__file__)
    context.request(
        DEFINITION,
        file="test",
        current_word="Bar",
        definition_starters=[
            (r"def ", "after"),
            (r"import .*,? ", "after"),
            (r"from ", "after"),
            (r"class ", "after"),
            (r":?.*=.*", "before"),
        ],
    )

    sleep(1)

    # Check output
    autocomplete_output: Response | None = context.get_response(AUTOCOMPLETE)
    if autocomplete_output is None:
        raise AssertionError("Autocomplete output is None")
    autocomplete_output["id"] = 0
    assert autocomplete_output == {
        "id": 0,
        "type": "response",
        "cancelled": False,
        "command": AUTOCOMPLETE,
        "result": ["test", "this"],
    }

    replacements_output: Response | None = context.get_response(REPLACEMENTS)
    if replacements_output is None:
        raise AssertionError("Replacements output is None")
    replacements_output["id"] = 0
    assert replacements_output == {
        "id": 0,
        "type": "response",
        "cancelled": False,
        "command": REPLACEMENTS,
        "result": ["this"],
    }

    highlight_output: Response | None = context.get_response(HIGHLIGHT)
    if highlight_output is None:
        raise AssertionError("Highlight output is None")
    highlight_output["id"] = 0
    assert highlight_output == {
        "id": 0,
        "type": "response",
        "cancelled": False,
        "command": HIGHLIGHT,
        "result": [
            ((1, 0), 4, "Keyword"),
            ((1, 5), 4, "Name"),
            ((1, 10), 6, "Keyword"),
            ((1, 17), 1, "Name"),
            ((1, 20), 12, "Comment"),
            ((3, 0), 3, "Name"),
            ((3, 4), 1, "Operator"),
            ((3, 6), 3, "Name"),
            ((3, 11), 7, "Comment"),
            ((5, 0), 5, "Name"),
            ((5, 5), 1, "Punctuation"),
            ((5, 6), 1, "String"),
            ((5, 7), 1, "String"),
            ((5, 8), 1, "String"),
            ((5, 9), 1, "Punctuation"),
            ((5, 12), 16, "Comment"),
            ((8, 0), 5, "Keyword"),
            ((8, 6), 3, "Name"),
            ((8, 9), 1, "Punctuation"),
            ((8, 10), 3, "Name"),
            ((8, 13), 1, "Punctuation"),
            ((8, 14), 1, "Punctuation"),
            ((9, 4), 3, "String"),
            ((10, 4), 4, "Name"),
            ((11, 4), 3, "String"),
            ((13, 4), 3, "Keyword"),
            ((13, 8), 8, "Name"),
            ((13, 16), 1, "Punctuation"),
            ((13, 17), 4, "Name"),
            ((13, 21), 1, "Punctuation"),
            ((13, 22), 1, "Punctuation"),
            ((14, 8), 4, "Keyword"),
            ((17, 0), 3, "Name"),
            ((17, 3), 1, "Punctuation"),
            ((17, 4), 1, "Punctuation"),
            ((18, 0), 24, "Comment"),
            ((9, 4), 3, "String"),
            ((10, 4), 4, "String"),
            ((11, 4), 3, "String"),
            ((18, 2), 22, "Link"),
            ((5, 7), 1, "Hidden_Char"),
        ],
    }

    context.remove_file("test")
    context.kill_IPC()


if __name__ == "__main__":
    test_IPC()
