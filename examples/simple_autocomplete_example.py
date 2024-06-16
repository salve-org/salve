from time import sleep

from salve_ipc import IPC, Response


def main():
    context = IPC()

    context.update_file(
        "test",
        open(__file__, "r+").read(),
    )

    context.request_autocomplete(
        file="test",
        expected_keywords=[],
        current_word="t",
    )

    sleep(1)

    output: Response = context.get_autocomplete_response()  # type: ignore
    print(output["result"])  # type: ignore
    context.kill_IPC()


if __name__ == "__main__":
    main()
