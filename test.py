from time import sleep

from salve_ipc import HIGHLIGHT, IPC


def main():
    """test"""
    context = IPC()

    context.update_file(
        "test",
        """def main():
    \"\"\"test\"\"\"
    \"\"\"
    test
    \"\"\" test
    r\"\"\"test\"\"\"
""",
    )

    context.request(
        HIGHLIGHT, file="test", language="python", text_range=(1, 30)
    )

    sleep(1)
    context.kill_IPC()


if __name__ == "__main__":
    main()
