from json import dumps, loads
from os import set_blocking
from random import randint
from subprocess import PIPE, Popen
from tkinter import Entry, Event, Label, Tk

used_ids: list[int] = []
current_id: int = 0


def create_server() -> Popen:
    server: Popen = Popen(["python3", "simple_server.py"], stdin=PIPE, stdout=PIPE)
    set_blocking(server.stdout.fileno(), False)  # type: ignore
    set_blocking(server.stdin.fileno(), False)  # type: ignore
    return server


app = Tk()
main_server: Popen = create_server()


def read_server_output() -> None:
    global main_server
    if main_server.poll():
        main_server = create_server()

    server_stdout = main_server.stdout

    for line in server_stdout:  # type: ignore
        global current_id
        response_json: dict = loads(line)
        id = response_json["id"]
        used_ids.remove(id)

        if id != current_id:
            continue

        current_id = 0
        item = response_json["item"]
        output_label.configure(text=f"Item at index requested: {item}")

    refresh_server()
    app.after(50, read_server_output)


def refresh_server() -> None:
    create_request(Event(), "refresh")


def create_request(_: Event, type: str = "request") -> None:
    global current_id
    id = randint(0, 5000)
    while id in used_ids:
        id = randint(0, 5000)

    used_ids.append(id)
    if type != "refresh":
        current_id = id  # We don't care for refresh request data

    request = dumps({"id": id, "type": type, "index": user_entry.get()})
    server_stdin = main_server.stdin
    if server_stdin is not None:
        server_stdin.write(f"{request}\n".encode())
        server_stdin.flush()


user_entry = Entry(app)
user_entry.pack()
user_entry.bind("<Return>", create_request)
user_entry.focus()

output_label = Label(app, text="Item at index ?: ?")
output_label.pack()

app.after_idle(read_server_output)

app.mainloop()
