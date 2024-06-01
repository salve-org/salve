from time import sleep

from salve_ipc import IPC, Response

context = IPC()

context.update_file(
    "test",
    open(__file__, "r+").read(),
)

context.request(
    "replacements", file="test", expected_keywords=[], current_word="contest"
)

sleep(1)
output: Response | None = context.get_response("replacements")
print(output["result"])  # type: ignore
context.kill_IPC()
