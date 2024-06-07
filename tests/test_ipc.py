from json import loads
from time import sleep

from salve_ipc import IPC, Response


def test_IPC():
    context = IPC()

    context.ping()

    context.update_file("test", open("tests/test_file.py", "r+").read())

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

    sleep(1)

    # Check output
    autocomplete_output: Response | None = context.get_response("autocomplete")
    assert autocomplete_output == {
        "cancelled": False,
        "command": "autocomplete",
        "result": ["this"],
    }

    replacements_output: Response | None = context.get_response("replacements")
    assert replacements_output == {
        "cancelled": False,
        "command": "replacements",
        "result": ["this"],
    }

    highlight_output: Response | None = context.get_response("highlight")
    # from json import dumps
    # json_file = "tests/highlight_output.json"
    # with open(json_file, "r+") as file:
    #     file.truncate()

    # print(
    #     dumps(highlight_output), file=open("tests/highlight_output.json", "r+")
    # )
    assert highlight_output == loads(
        open("tests/highlight_output.json").read()
    )

    assert context.check_server_error() == (False, "")

    context.remove_file("test")
    context.kill_IPC()


test_IPC()
