from time import sleep

from salve_ipc import IPC, Response

context = IPC()

context.update_file(
    "test",
    open(__file__, "r+").read(),
)

context.request("highlight", file="test", language="python")

sleep(1)
output: Response | None = context.get_response("highlight")
print(output["result"])  # type: ignore
context.kill_IPC()
