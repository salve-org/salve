from time import sleep

from salve import AUTOCOMPLETE, IPC, Response


def main():
    context = IPC()

    context.update_file(
        "test",
        open(__file__, "r+").read(),
    )

    context.request(
        AUTOCOMPLETE,
        file="test",
        expected_keywords=[],
        current_word="t",
    )

    sleep(1)

    output: Response | None = context.get_response(AUTOCOMPLETE)  # type: ignore
    print(output)
    context.kill_IPC()


if __name__ == "__main__":
    main()
