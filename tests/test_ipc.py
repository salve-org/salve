from pathlib import Path
from time import sleep

from salve import (
    AUTOCOMPLETE,
    DEFINITION,
    EDITORCONFIG,
    HIGHLIGHT,
    IPC,
    LINKS_AND_CHARS,
    REPLACEMENTS,
    Response,
)


def test_IPC():
    context = IPC()

    context.update_file(
        "test", open(Path("tests/testing_file1.py"), "r+").read()
    )
    context.update_file("hidden_test", "https://www.google.com  (​)")

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
    context.request(
        HIGHLIGHT, file="test", language="python", text_range=(1, 18)
    )
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
    context.request(LINKS_AND_CHARS, file="hidden_test", text_range=(1, 18))
    sleep(1)

    # Check output
    autocomplete_output: Response | None = context.get_response(AUTOCOMPLETE)  # type: ignore
    if autocomplete_output is None:
        raise AssertionError("Autocomplete output is None")
    autocomplete_output["id"] = 0
    assert autocomplete_output == {
        "id": 0,
        "type": "response",
        "cancelled": False,
        "command": "autocomplete",
        "result": ["test", "this", "type"],
    }

    replacements_output: Response | None = context.get_response(REPLACEMENTS)  # type: ignore
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

    highlight_output: Response | None = context.get_response(HIGHLIGHT)  # type: ignore
    if highlight_output is None:
        raise AssertionError("Highlight output is None")
    highlight_output["id"] = 0
    expected_output: Response = {
        "id": 0,
        "type": "response",
        "cancelled": False,
        "command": "highlight",
        "result": [
            ((1, 0), 4, "Keyword"),
            ((1, 5), 4, "Identifier"),
            ((1, 10), 6, "Keyword"),
            ((1, 17), 1, "Identifier"),
            ((1, 20), 12, "Comment"),
            ((3, 0), 3, "Identifier"),
            ((3, 3), 1, "Punctuation"),
            ((3, 5), 4, "Identifier"),
            ((3, 10), 1, "Operator"),
            ((3, 12), 3, "Identifier"),
            ((4, 0), 1, "Punctuation"),
            ((4, 1), 3, "Identifier"),
            ((4, 5), 2, "Operator"),
            ((4, 8), 4, "Identifier"),
            ((4, 12), 1, "Punctuation"),
            ((4, 15), 12, "Comment"),
            ((6, 0), 5, "Identifier"),
            ((6, 5), 2, "Punctuation"),
            ((9, 0), 5, "Keyword"),
            ((9, 6), 3, "Identifier"),
            ((9, 9), 1, "Punctuation"),
            ((9, 10), 3, "Identifier"),
            ((9, 13), 2, "Punctuation"),
            ((10, 4), 3, "String"),
            ((11, 4), 4, "String"),
            ((12, 4), 3, "String"),
            ((14, 4), 3, "Keyword"),
            ((14, 8), 8, "Identifier"),
            ((14, 16), 1, "Punctuation"),
            ((14, 17), 4, "Identifier"),
            ((14, 21), 2, "Punctuation"),
            ((15, 8), 4, "Keyword"),
            ((18, 0), 3, "Identifier"),
            ((18, 3), 2, "Punctuation"),
        ],
    }

    assert highlight_output == expected_output

    links_and_hidden_chars_result: Response | None = context.get_response(
        LINKS_AND_CHARS
    )  # type: ignore
    if links_and_hidden_chars_result is None:
        raise AssertionError("links_and_hidden_chars_result output is None")
    links_and_hidden_chars_result["id"] = 0
    expected_output = {
        "id": 0,
        "type": "response",
        "cancelled": False,
        "command": LINKS_AND_CHARS,
        "result": [((1, 0), 22, "Link"), ((1, 25), 1, "Hidden_Char")],
    }
    assert links_and_hidden_chars_result == expected_output

    context.update_file(
        "foo", open(Path("tests/testing_file2.py"), "r+").read()
    )
    context.request(HIGHLIGHT, file="foo", language="python")
    while not (output := context.get_response(HIGHLIGHT)):
        pass
    response = output["result"]  # type: ignore
    assert response != []

    context.remove_file("test")
    context.kill_IPC()


if __name__ == "__main__":
    test_IPC()
