from tkinter import Entry, Label, Tk

from salve_ipc import IPC, Response

# Create context for IPC
context = IPC()

# Create window
root = Tk()


def create_request(_) -> None:
    context.update_file("test", e.get())
    context.request(
        "autocomplete",
        expected_keywords=[],
        file="test",
        current_word=e.get()[-1],
    )


# Create entry and label
e = Entry(root)
e.pack()
e.bind("<Return>", create_request)

l = Label(root, text="")
l.pack()


def ping_loop() -> None:
    context.ping()
    output: Response | None = context.get_response("autocomplete")
    data: list[str] = [""]
    if output is not None:
        data: list[str] = output["result"]  # type: ignore
        if not data:
            data = [""]
        l.configure(text=str(data))
    root.after(50, ping_loop)


root.after_idle(ping_loop)
root.mainloop()
