from time import sleep

from salve_ipc import IPC, Response

context = IPC()

context.add_file(
    "test", "test file with testing words which should return test then testing"
)

context.request(
    "autocomplete",
    file="test",
    expected_keywords=[],
    current_word="t",
)

sleep(1)

output: Response = context.get_response()  # type: ignore
print(output)
