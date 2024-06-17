from time import sleep

from salve_ipc import IPC, Response
from salve_ipc.misc import EDITORCONFIG


def main():
    context = IPC()

    context.request(EDITORCONFIG, file_path=__file__)

    sleep(1)
    output: Response | None = context.get_response(EDITORCONFIG)
    print(output)
    context.kill_IPC()


if __name__ == "__main__":
    main()
