from time import sleep

from salve import IPC, LINKS_AND_CHARS, Response


def main():
    context = IPC()

    context.update_file(
        "test",
        open(__file__, "r+").read(),
    )

    context.request(LINKS_AND_CHARS, file="test", text_range=(1, 30))

    sleep(1)
    output: Response | None = context.get_response(LINKS_AND_CHARS)  # type: ignore
    print(output)
    context.kill_IPC()


if __name__ == "__main__":
    main()
