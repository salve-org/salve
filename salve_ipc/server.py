from json import dumps, loads
from os import set_blocking
from selectors import EVENT_READ, DefaultSelector
from sys import exit, stdin, stdout
from time import time

from highlight import Token, get_highlights
from misc import COMMANDS, Details, Message, Notification, Request, Response
from server_functions import find_autocompletions, get_replacements


class Handler:
    """Handles input from the user and returns output from special functions designed to make the job easy. Not an external API."""

    def __init__(self) -> None:
        set_blocking(stdin.fileno(), False)
        set_blocking(stdout.fileno(), False)
        self.selector = DefaultSelector()
        self.selector.register(stdin, EVENT_READ)

        self.all_ids: dict[int, str] = {}  # id, tmp path
        self.newest_ids: dict[str, int] = {}
        self.newest_requests: dict[str, Request | None] = {}
        for command in COMMANDS:
            self.newest_ids[command] = 0
            self.newest_requests[command] = None

        self.files: dict[str, str] = {}

        self.old_time = time()

    def write_tmp_file(self, details: Details, tmp_path: str) -> None:
        with open(tmp_path, "r+") as file:
            file.truncate()
            file.write(dumps(details))
            file.flush()

    def write_message(self, message: Message) -> None:
        stdout.write(dumps(message) + "\n")
        stdout.flush()

    def simple_id_response(
        self, id: int, tmp_path: str, cancelled: bool = True
    ) -> None:
        response_details: Response = {
            "cancelled": cancelled,
        }
        response: Message = {
            "id": id,
            "type": "response",
            "tmp_file": tmp_path,
        }
        self.write_tmp_file(response_details, tmp_path)
        self.write_message(response)

    def parse_line(self, line: str) -> None:
        json_input: Message = loads(line)
        id: int = json_input["id"]
        match json_input["type"]:
            case "ping":
                self.simple_id_response(id, json_input["tmp_file"], False)
            case "notification":
                notification_details: Notification = loads(
                    open(json_input["tmp_file"], "r+").read()
                )
                filename: str = notification_details["file"]
                if notification_details["remove"]:
                    self.files.pop(filename)
                    return
                contents: str = notification_details["contents"]  # type: ignore
                self.files[filename] = contents
                self.simple_id_response(id, json_input["tmp_file"], False)
            case _:
                request_details: Request = loads(
                    open(json_input["tmp_file"], "r+").read()
                )
                self.all_ids[id] = json_input["tmp_file"]
                command: str = request_details["command"]  # type: ignore
                self.newest_ids[command] = id
                self.newest_requests[command] = request_details  # type: ignore

    def cancel_all_ids_except_newest(self) -> None:
        for id in list(self.all_ids.keys()):
            if id in list(self.newest_ids.values()):
                continue
            self.simple_id_response(id, self.all_ids.pop(id))

    def handle_request(self, request: Request) -> None:
        command: str = request["command"]
        id: int = self.newest_ids[command]
        file: str = request["file"]
        result: list[str | tuple[tuple[int, int], int, str]] = []
        cancelled: bool = False
        tmp_file: str = self.all_ids.pop(id)

        match request["command"]:
            case "autocomplete":
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
                result += [token.to_tuple() for token in pre_refined_result]  # type: ignore
            case _:
                cancelled = True

        response_details: Response = {
            "cancelled": cancelled,
            "command": command,
            "result": result,  # type: ignore
        }
        response_message: Message = {
            "id": id,
            "type": "response",
            "tmp_file": tmp_file,
        }
        self.write_tmp_file(response_details, response_message["tmp_file"])
        self.write_message(response_message)
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


if __name__ == "__main__":
    handler = Handler()
    while True:
        handler.run_tasks()
