from time import sleep

from salve_ipc import IPC, Response


def main():
    context = IPC()

    context.update_file(
        "test",
        open(__file__, "r+").read() * 20,
    )

    context.request_highlight(
        file="test", language="python", text_range=(1, 30)
    )

    sleep(1)
    output: Response | None = context.get_highlight_response()
    print(output["result"])  # type: ignore
    context.kill_IPC()


if __name__ == "__main__":
    main()
