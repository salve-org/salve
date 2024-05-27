from time import sleep

from salve_ipc import IPC, Response

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
print(output)
