from time import sleep

from salve_ipc import IPC, Response


def main():
    context = IPC()

    context.update_file("test", open(__file__, "r+").read())

    context.request_definition(
        file="test",
        current_word="context",
        definition_starters=[
            (r"def ", "after"),
            (r"import .*,? ", "after"),
            (r"from ", "after"),
            (r"class ", "after"),
            (r":?.*=.*", "ahead"),
        ],  # Every way to define a variable, class, namespace, etc in Python (regex)
    )

    sleep(1)
    output: Response | None = context.get_definition_response()
    print(output["result"])  # type: ignore
    context.kill_IPC()


if __name__ == "__main__":
    main()
