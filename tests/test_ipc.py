from time import sleep

from salve_ipc import IPC, Response


def test_IPC():
    autocompleter = IPC()

    autocompleter.ping()

    autocompleter.update_file("test.py", "testy\n")

    autocompleter.request(
        "autocomplete",
        expected_keywords=[],
        file="test.py",
        current_word="t",
    )

    sleep(1)

    # Check output
    output: Response = autocompleter.get_response("autocomplete")  # type: ignore
    output["id"] = 0
    assert output == {
        "id": 0,
        "type": "response",
        "cancelled": False,
        "command": "autocomplete",
        "result": ["testy"],
    }

    autocompleter.remove_file("test.py")


test_IPC()
