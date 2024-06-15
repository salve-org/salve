from time import sleep

from salve_ipc import IPC, Response


def main():
    context = IPC()

    context.update_file("test", open(__file__, "r+").read())

    context.request(
        "definition",
        file="test",
        current_word="context",
        definition_starters=[
            (r"def ", "after"),
            (r"import .*,? ", "after"),
            (r"from ", "after"),
            (r"class ", "after"),
            (r":?.*=.*", "ahead"),
        ],
    )

    sleep(1)
    output: Response | None = context.get_response("definition")
    print(output["result"])  # type: ignore
    context.kill_IPC()


if __name__ == "__main__":
    main()
