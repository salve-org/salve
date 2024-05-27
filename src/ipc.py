from difflib import ndiff
from json import dumps, loads
from os import set_blocking
from pathlib import Path
from random import randint
from subprocess import PIPE, Popen
from typing import IO

from .message import AutocompleteRequest, Message, Notification, Ping, Response


class IPC:
    def __init__(self, id_max: int = 5_000) -> None:
        self.used_ids: list[int] = []
        self.current_id = 0
        self.id_max = id_max

        self.newest_response: Response | None = None

        self.files: dict[str, str] = {}

        self.main_server: Popen
        self.create_server()

    def create_server(self) -> None:
        server_file: Path = Path(__file__).parent / "server.py"
        server = Popen(["python3", str(server_file)], stdin=PIPE, stdout=PIPE)
        set_blocking(server.stdout.fileno(), False)  # type: ignore
        set_blocking(server.stdin.fileno(), False)  # type: ignore
        self.main_server = server

        for filename in self.files.keys():
            data: str = self.files.pop(filename)
            self.add_file(filename, data)

    def check_server(self) -> None:
        if self.main_server.poll() is not None:
            self.create_server()

    def get_server_file(self, file: str) -> IO:
        self.check_server()
        if file == "stdout":
            return self.main_server.stdout  # type: ignore
        return self.main_server.stdin  # type: ignore

    def send_message(self, message: Message) -> None:
        json_request: str = dumps(message)

        server_stdin = self.get_server_file("stdin")
        server_stdin.write(f"{json_request}\n".encode())
        server_stdin.flush()

    def create_message(self, type: str = "request", **kwargs) -> None:
        id = randint(0, self.id_max)
        while id in self.used_ids:
            id = randint(0, self.id_max)

        self.used_ids.append(id)
        match type:
            case "ping":
                ping: Ping = {"id": id, "type": "ping"}
                self.send_message(ping)
            case "request":
                self.current_id = id
                request: AutocompleteRequest = {
                    "id": id,
                    "type": type,
                    "form": kwargs.get("type", "autocomplete"),
                    "expected_keywords": kwargs.get("expected_keywords", []),
                    "full_text": kwargs.get("full_text", ""),
                    "current_word": kwargs.get("current_word", ""),
                }
                self.send_message(request)
            case "notify":
                notification: Notification = {
                    "id": id,
                    "type": type,
                    "remove": True,
                    "filename": kwargs.get("filename", ""),
                }

                if kwargs.get("remove", False):
                    notification["remove"] = False
                    notification["diff"] = kwargs.get("diff", "")

                self.send_message(notification)

    def ping(self) -> None:
        self.create_message("ping")

    def request(self, type: str = "autocomplete", **kwargs) -> None:
        self.create_message(
            form=type,
            expected_keywords=kwargs.get("expected_keywords", []),
            full_text=kwargs.get("full_text", ""),
            current_word=kwargs.get("current_word", ""),
        )

    def parse_line(self, line: str) -> None:
        response_json: Response = loads(line)
        id = response_json["id"]
        self.used_ids.remove(id)

        if id != self.current_id:
            return

        self.current_id = 0
        self.newest_response = response_json

    def check_responses(self, type: str = "autocomplete") -> None:
        server_stdout: IO = self.get_server_file("stdout")

        for line in server_stdout:  # type: ignore
            self.parse_line(line)

    def get_response(self, type: str = "autocomplete") -> Response | None:
        self.check_responses()
        response: Response | None = self.newest_response
        self.newest_response = None
        return response

    def add_file(self, filename: str, current_state: str) -> None:
        if filename in self.files.keys():
            return

        self.files[filename] = current_state

        diff = "".join(ndiff([""], current_state.splitlines(keepends=True)))

        self.create_message("notification", filename=filename, diff=diff)

    def update_file(self, filename: str, current_state: str) -> None:
        self.add_file(filename, current_state)

        self.files[filename] = current_state

        diff = "".join(
            ndiff(
                self.files[filename].splitlines(keepends=True),
                current_state.splitlines(keepends=True),
            )
        )
        self.create_message("notification", filename=filename, diff=diff)

    def remove_file(self, filename: str) -> None:
        if filename not in self.files.keys():
            raise Exception(
                f"Cannot remove file {filename} when file not in self.files!"
            )
        self.create_message("notification", remove=True, filename=filename)
