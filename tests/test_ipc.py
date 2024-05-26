from salve import IPC, Response
from time import sleep


def test_IPC():
    autocompleter = IPC()

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
