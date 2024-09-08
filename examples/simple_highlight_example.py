from time import sleep

from salve import HIGHLIGHT, IPC, Response


def main():
    context = IPC()

    context.update_file(
        "test",
        open(__file__, "r+").read(),
    )

    context.request(
        HIGHLIGHT, file="test", language="python", text_range=(1, 30)
    )

    sleep(1)
    output: Response | None = context.get_response(HIGHLIGHT)  # type: ignore
    print(output)
    context.kill_IPC()


if __name__ == "__main__":
    main()
