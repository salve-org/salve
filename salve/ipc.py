from json import dumps, loads
from os import set_blocking
from random import randint
from subprocess import PIPE, Popen
from typing import IO
from .message import Message, Ping, Request, Response
from pathlib import Path


class IPC:
    def __init__(self, id_max: int = 5_000) -> None:
        self.used_ids: list[int] = []
        self.current_id = 0
        self.newest_response: dict[str, None | Response] = {"autocomplete": None}
        self.id_max = id_max
        self.main_server: Popen
        self.create_server()

    def create_server(self) -> None:
        server_file: Path = Path(__file__).parent / "server.py"
        server = Popen(["python3", str(server_file)], stdin=PIPE, stdout=PIPE)
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
        if type == "ping":
            ping: Ping = {"id": id, "type": "ping"}
            self.send_message(ping)
            return

        self.current_id = id  # We don't care for ping responses
        request: Request = {
            "id": id,
            "type": type,
            "form": kwargs.get("type", "autocomplete"),
            "expected_keywords": kwargs.get("expected_keywords", []),
            "full_text": kwargs.get("full_text", ""),
            "current_word": kwargs.get("current_word", ""),
        }
        self.send_message(request)

    def ping(self) -> None:
        self.create_message("ping")

    def request(self, type: str = "autocomplete", **kwargs) -> None:
        self.create_message(
            type=type,
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
        self.newest_response["autocomplete"] = response_json

    def has_response(self, type: str = "autocomplete") -> bool:
        server_stdout: IO = self.get_server_file("stdout")

        for line in server_stdout:  # type: ignore
            self.parse_line(line)

        if self.newest_response["autocomplete"]:
            return True

        return False

    def get_response(self, type: str = "autocomplete") -> Response | None:
        response: Response | None = self.newest_response["autocomplete"]
        self.newest_response["autocomplete"] = None
        return response
