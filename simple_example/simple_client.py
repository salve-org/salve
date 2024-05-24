from json import dumps, loads
from os import set_blocking
from random import randint
from subprocess import PIPE, Popen
from tkinter import Entry, Event, Label, Tk
from typing import IO


class ServerApp:
    def __init__(self):
        self.used_ids = []
        self.current_id = 0
        self.main_server: Popen
        self.create_server()

        self.app = Tk()
        self.user_entry = Entry(self.app)
        self.user_entry.pack()
        self.user_entry.bind("<Return>", self.create_request)
        self.user_entry.focus()

        self.output_label = Label(self.app, text="Item at index ?: ?")
        self.output_label.pack()

        self.app.after_idle(self.read_server_output)
        self.app.mainloop()

    def create_server(self) -> None:
        server = Popen(["python3", "simple_server.py"], stdin=PIPE, stdout=PIPE)
        set_blocking(server.stdout.fileno(), False)  # type: ignore
        set_blocking(server.stdin.fileno(), False)  # type: ignore
        self.main_server = server

    def check_server(self) -> None:
        if self.main_server.poll():
            self.create_server()

    def get_server_file(self, file: str) -> IO:
        self.check_server()
        if file == "stdout":
            return self.main_server.stdout  # type: ignore
        return self.main_server.stdin  # type: ignore

    def parse_line(self, line: str) -> None:
        response_json = loads(line)
        id = response_json["id"]
        self.used_ids.remove(id)

        if id != self.current_id:
            return

        self.current_id = 0
        item = response_json["item"]  # type: ignore
        self.output_label.configure(text=f"Item at index requested: {item}")

    def read_server_output(self) -> None:
        server_stdout: IO = self.get_server_file("stdout")

        for line in server_stdout:  # type: ignore
            self.parse_line(line)

        self.refresh_server()
        self.app.after(50, self.read_server_output)

    def refresh_server(self) -> None:
        self.create_request(Event(), "refresh")

    def create_request(self, _: Event, type: str = "request") -> None:
        id = randint(0, 5000)
        while id in self.used_ids:
            id = randint(0, 5000)

        self.used_ids.append(id)
        if type != "refresh":
            self.current_id = id  # We don't care for refresh request data

        request = dumps({"id": id, "type": type, "index": self.user_entry.get()})

        server_stdin = self.get_server_file("stdin")

        server_stdin.write(f"{request}\n".encode())
        server_stdin.flush()


if __name__ == "__main__":
    ServerApp()
