from difflib import ndiff
from json import dumps, loads
from os import set_blocking
from pathlib import Path
from random import randint
from subprocess import PIPE, Popen
from typing import IO

from .misc import COMMANDS, Message, Notification, Ping, Request, Response


class IPC:
    def __init__(self, id_max: int = 15_000) -> None:
        self.used_ids: list[int] = []
        self.id_max = id_max
        self.current_ids: dict[str, int] = {}
        self.newest_responses: dict[str, Response | None] = {}
        for command in COMMANDS:
            self.current_ids[command] = 0
            self.newest_responses[command] = None

        self.files: dict[str, str] = {}

        self.main_server: Popen
        self.create_server()

    def create_server(self) -> None:
        server_file: Path = Path(__file__).parent / "server.py"
        server = Popen(["python3", str(server_file)], stdin=PIPE, stdout=PIPE)
        set_blocking(server.stdout.fileno(), False)  # type: ignore
        set_blocking(server.stdin.fileno(), False)  # type: ignore
        self.main_server = server

        files_copy = self.files.copy()
        self.files = {}
        for filename, data in files_copy.items():
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

    def create_message(self, type: str, **kwargs) -> None:
        id = randint(1, self.id_max)  # 0 is reserved for the empty case
        while id in self.used_ids:
            id = randint(1, self.id_max)

        self.used_ids.append(id)
        match type:
            case "ping":
                ping: Ping = {"id": id, "type": "ping"}
                self.send_message(ping)
            case "request":
                command = kwargs.get("command", "")
                if command not in COMMANDS:
                    raise Exception(f"Cannot execute command {command}")
                self.current_ids[command] = id
                request: Request = {
                    "id": id,
                    "type": type,
                    "command": command,
                    "file": kwargs.get("file"),
                    "expected_keywords": kwargs.get("expected_keywords"),
                    "current_word": kwargs.get("current_word"),
                    "language": kwargs.get("language")
                } # type: ignore
                self.send_message(request)
            case "notification":
                notification: Notification = {
                    "id": id,
                    "type": type,
                    "remove": kwargs.get("remove", False),
                    "filename": kwargs.get("filename", ""),
                    "diff": kwargs.get("diff", ""),
                }
                self.send_message(notification)
            case _:
                ping: Ping = {"id": id, "type": "ping"}
                self.send_message(ping)

    def ping(self) -> None:
        self.create_message("ping")

    def request(
        self,
        command: str,
        file: str,
        expected_keywords: list[str] = [""],
        current_word: str = "",
        language: str = "Text"
    ) -> None:
        self.create_message(
            type="request",
            command=command,
            file=file,
            expected_keywords=expected_keywords,
            current_word=current_word,
            language = language
        )

    def cancel_request(self, command: str):
        if command not in COMMANDS:
            raise Exception(f"Cannot execute command {command}")

        self.current_ids[command] = 0

    def parse_line(self, line: str) -> None:
        response_json: Response = loads(line)
        id = response_json["id"]
        self.used_ids.remove(id)

        if "command" not in response_json:
            return

        command = response_json["command"]
        if id != self.current_ids[command]:
            return

        self.current_ids[command] = 0
        self.newest_responses[command] = response_json

    def check_responses(self) -> None:
        server_stdout: IO = self.get_server_file("stdout")

        for line in server_stdout:  # type: ignore
            self.parse_line(line)

    def get_response(self, command: str) -> Response | None:
        if command not in COMMANDS:
            raise Exception(f"Command {command} not in COMMANDS")
        self.check_responses()
        response: Response | None = self.newest_responses[command]
        if response is None:
            return None
        self.newest_responses[command] = None
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
        self.create_message("notification", remove=True, filename=filename)

    def kill_IPC(self) -> None:
        self.main_server.kill()
