from time import sleep

from salve_ipc import IPC, Response
from salve_ipc.misc import REPLACEMENTS


def main():
    context = IPC()

    context.update_file(
        "test",
        open(__file__, "r+").read(),
    )

    context.request(
        REPLACEMENTS,
        file="test",
        expected_keywords=[],
        current_word="contest",
    )

    sleep(1)
    output: Response | None = context.get_response(REPLACEMENTS)
    print(output)
    context.kill_IPC()


if __name__ == "__main__":
    main()
