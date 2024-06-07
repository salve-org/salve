from time import sleep

from salve_ipc import IPC, Response

context = IPC()

context.update_file(
    "test",
    open(__file__, "r+").read(),
)

context.request("highlight", file="test", language="python", text_range=(1, 5))

sleep(1)
output: Response | None = context.get_response("highlight")
print(context.main_server.stderr.read().decode())  # type: ignore
print(output["result"])  # type: ignore
context.kill_IPC()
