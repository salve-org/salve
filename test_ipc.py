from time import sleep

from src import IPC, Response


def test_IPC():
    autocompleter = IPC()

    autocompleter.ping()

    autocompleter.add_file("test.py", "test\n")
    autocompleter.update_file("test.py", "testy\n")
    autocompleter.remove_file("test.py")

    autocompleter.request(
        "autocomplete",
        expected_keywords=[],
        full_text="test",
        current_word="t",
    )

    sleep(1)

    # Check output
    output: Response = autocompleter.get_response()  # type: ignore
    output["id"] = 0
    assert output == {
        "id": 0,
        "type": "response",
        "cancelled": False,
        "autocomplete": ["test"],
    }


test_IPC()
