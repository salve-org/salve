from time import sleep

from salve_ipc import IPC, Response
from salve_ipc.misc import AUTOCOMPLETE


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

    output: Response | None = context.get_response(AUTOCOMPLETE)
    print(output)
    context.kill_IPC()


if __name__ == "__main__":
    main()
