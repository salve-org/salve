from tkinter import Entry, Label, Tk

from salve_ipc import IPC, Response
from salve_ipc.misc import AUTOCOMPLETE


def main():
    # Create context for IPC
    context = IPC()

    # Create window
    root = Tk()

    def create_request(_) -> None:
        context.update_file("test", entry.get())
        context.request(
            AUTOCOMPLETE,
            expected_keywords=[],
            file="test",
            current_word=entry.get()[-1],
        )

    # Create entry and label
    entry = Entry(root)
    entry.pack()
    entry.bind("<Return>", create_request)

    label = Label(root, text="")
    label.pack()

    def loop() -> None:
        output: Response | None = context.get_response(AUTOCOMPLETE)
        data: list[str] = [""]
        if output is not None:
            data: list[str] = output["result"]  # type: ignore
            if not data:
                data = [""]
            label.configure(text=str(data))
        root.after(50, loop)

    root.after_idle(loop)
    root.mainloop()
    context.kill_IPC()


if __name__ == "__main__":
    main()
