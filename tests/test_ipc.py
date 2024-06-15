from time import sleep

from salve_ipc import IPC, Response


def test_IPC():
    context = IPC()

    context.update_file("test", open("tests/testing_file1.py", "r+").read())

    context.request(
        "autocomplete",
        file="test",
        expected_keywords=[],
        current_word="t",
    )
    context.request(
        "replacements",
        file="test",
        expected_keywords=[],
        current_word="thid",
    )
    context.request("highlight", file="test", language="python")
    context.request("editorconfig", file="test", file_path=__file__)
    context.request(
        "definition",
        file="test",
        current_word="Bar",
        definition_starters=[
            (r"def ", "after"),
            (r"import .*,? ", "after"),
            (r"from ", "after"),
            (r"class ", "after"),
            (r":?.*=.*", "ahead"),
        ],
    )

    sleep(1)

    # Check output
    autocomplete_output: Response | None = context.get_response("autocomplete")
    if autocomplete_output is None:
        raise AssertionError("Autocomplete output is None")
    autocomplete_output["id"] = 0
    assert autocomplete_output == {
        "id": 0,
        "type": "response",
        "cancelled": False,
        "command": "autocomplete",
        "result": ["this"],
    }

    replacements_output: Response | None = context.get_response("replacements")
    if replacements_output is None:
        raise AssertionError("Replacements output is None")
    replacements_output["id"] = 0
    assert replacements_output == {
        "id": 0,
        "type": "response",
        "cancelled": False,
        "command": "replacements",
        "result": ["this"],
    }

    highlight_output: Response | None = context.get_response("highlight")
    if highlight_output is None:
        raise AssertionError("Highlight output is None")
    highlight_output["id"] = 0
    assert highlight_output == {
        "id": 0,
        "type": "response",
        "cancelled": False,
        "command": "highlight",
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
            ((9, 4), 3, "Keyword"),
            ((9, 8), 8, "Name"),
            ((9, 16), 1, "Punctuation"),
            ((9, 17), 4, "Name"),
            ((9, 21), 1, "Punctuation"),
            ((9, 22), 1, "Punctuation"),
            ((10, 8), 4, "Keyword"),
            ((13, 0), 3, "Name"),
            ((13, 3), 1, "Punctuation"),
            ((13, 4), 1, "Punctuation"),
            ((14, 0), 24, "Comment"),
            ((14, 2), 22, "Link"),
            ((5, 7), 1, "Hidden_Char"),
        ],
    }

    editorconfig_response: Response | None = context.get_response(
        "editorconfig"
    )
    if editorconfig_response is None:
        raise AssertionError("Editorconfig output is None")
    editorconfig_response["id"] = 0
    assert editorconfig_response == {
        "id": 0,
        "type": "response",
        "cancelled": False,
        "command": "editorconfig",
        "result": {
            "end_of_line": "lf",
            "insert_final_newline": "true",
            "charset": "utf-8",
            "indent_style": "space",
            "indent_size": "4",
        },
    }

    definition_response: Response | None = context.get_response("definition")
    if definition_response is None:
        raise AssertionError("Definition output is None")
    definition_response["id"] = 0
    assert definition_response == {
        "id": 0,
        "type": "response",
        "cancelled": False,
        "command": "definition",
        "result": ((3, 0), 3, "Definition"),
    }

    context.remove_file("test")
    context.kill_IPC()


if __name__ == "__main__":
    test_IPC()
