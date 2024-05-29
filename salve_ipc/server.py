from difflib import restore
from json import dumps, loads
from os import set_blocking
from selectors import EVENT_READ, DefaultSelector
from sys import exit, stdin, stdout
from time import time

from misc import COMMANDS, Message, Request, Response
from server_functions import (
    Token,
    find_autocompletions,
    get_highlights,
    get_replacements,
)


class Handler:
    def __init__(self) -> None:
        set_blocking(stdin.fileno(), False)
        set_blocking(stdout.fileno(), False)
        self.selector = DefaultSelector()
        self.selector.register(stdin, EVENT_READ)

        self.id_list: list[int] = []
        self.newest_ids: dict[str, int] = {}
        self.newest_requests: dict[str, Request | None] = {}
        for command in COMMANDS:
            self.newest_ids[command] = 0
            self.newest_requests[command] = None

        self.files: dict[str, str] = {}

        self.old_time = time()

    def write_response(self, response: Response) -> None:
        stdout.write(dumps(response) + "\n")
        stdout.flush()

    def cancel_id(self, id: int) -> None:
        response: Response = {"id": id, "type": "response", "cancelled": True}
        self.write_response(response)

    def parse_line(self, line: str) -> None:
        json_input: Message = loads(line)
        id: int = json_input["id"]
        match json_input["type"]:
            case "ping":
                self.cancel_id(id)
            case "notification":
                filename: str = json_input["filename"]  # type: ignore
                if json_input["remove"]:  # type: ignore
                    self.files.pop(filename)
                    return
                diff: list[str] = json_input["diff"].splitlines()  # type: ignore
                self.files[filename] = "".join(restore(diff, 2))  # type: ignore
            case _:
                self.id_list.append(id)
                command: str = json_input["command"]  # type: ignore
                self.newest_ids[command] = id
                self.newest_requests[command] = json_input  # type: ignore

    def cancel_all_ids_except_newest(self) -> None:
        for id in self.id_list:
            if id in list(self.newest_ids.values()):
                continue
            self.cancel_id(id)

    def handle_request(self, request: Request) -> None:
        file: str = request["file"]
        result: list[str] = []
        command: str = request["command"]
        cancelled: bool = False

        if not file in self.files:
            response: Response = {
                "id": request["id"],
                "type": "response",
                "cancelled": True,
                "command": command,
                "result": result,
            }

        match request["command"]:
            case "autocomplete":
                result: list[str] = []
                result = find_autocompletions(
                    full_text=self.files[file],
                    expected_keywords=request["expected_keywords"],  # type: ignore
                    current_word=request["current_word"],  # type: ignore
                )
            case "replacements":
                result = get_replacements(
                    full_text=self.files[file],
                    expected_keywords=request["expected_keywords"],  # type: ignore
                    replaceable_word=request["current_word"],  # type: ignore
                )
            case "highlight":
                pre_refined_result: list[Token] = get_highlights(
                    full_text=self.files[file], language=request["language"]  # type: ignore
                )
                result = []
                result += [str(token) for token in pre_refined_result]
            case _:
                cancelled = True

        response: Response = {
            "id": request["id"],
            "type": "response",
            "cancelled": cancelled,
            "command": command,
            "result": result,
        }
        self.write_response(response)
        self.newest_ids[command] = 0

    def run_tasks(self) -> None:
        current_time = time()
        if current_time - self.old_time > 5:
            exit(0)

        events = self.selector.select(0.025)
        if not events:
            return

        for line in stdin:
            # Prevent zombie process
            if self.old_time != current_time:
                self.old_time = current_time

            self.parse_line(line)

        self.cancel_all_ids_except_newest()

        if not list(
            self.newest_requests.values()
        ):  # There may have only been refreshes
            return

        # Actual work
        for request in list(self.newest_requests.values()):
            if request is None:
                continue
            self.handle_request(request)
            command: str = request["command"]
            self.newest_requests[command] = None

        self.id_list = []


if __name__ == "__main__":
    handler = Handler()
    while True:
        handler.run_tasks()
