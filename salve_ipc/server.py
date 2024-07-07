from multiprocessing.connection import Connection
from multiprocessing.queues import Queue as GenericClassQueue
from sys import platform
from time import sleep

from pyeditorconfig import get_config

from .misc import (
    COMMANDS,
    Notification,
    Request,
    RequestQueueType,
    Response,
    ResponseQueueType,
)
from .server_functions import (
    Token,
    find_autocompletions,
    get_definition,
    get_highlights,
    get_replacements,
)

# Deal with Windows weirdness
if platform == "win32":
    from multiprocessing.connection import (
        PipeConnection as Connection,  # type: ignore
    )


class Server:
    """Handles input from the user and returns output from special functions designed to make the job easy. Not an external API."""

    def __init__(
        self,
        server_end: Connection,
        response_queue: GenericClassQueue,
        requests_queue: GenericClassQueue,
    ) -> None:
        self.server_end: Connection = server_end
        self.response_queue: ResponseQueueType = response_queue
        self.requests_queue: RequestQueueType = requests_queue
        self.all_ids: list[int] = []
        self.newest_ids: dict[str, int] = {}
        self.newest_requests: dict[str, Request | None] = {}
        for command in COMMANDS:
            self.newest_ids[command] = 0
            self.newest_requests[command] = None

        self.files: dict[str, str] = {}

        while True:
            self.run_tasks()
            sleep(0.0025)

    def simple_id_response(self, id: int, cancelled: bool = True) -> None:
        response: Response = {
            "id": id,
            "type": "response",
            "cancelled": cancelled,
        }
        self.response_queue.put(response)

    def parse_line(self, message: Request | Notification) -> None:
        id: int = message["id"]
        match message["type"]:
            case "notification":
                file: str = message["file"]  # type: ignore
                if message["remove"]:  # type: ignore
                    self.files.pop(file)
                    return
                contents: str = message["contents"]  # type: ignore
                self.files[file] = contents
                self.simple_id_response(id, False)
            case "request":
                self.all_ids.append(id)
                command: str = message["command"]  # type: ignore
                self.newest_ids[command] = id
                self.newest_requests[command] = message  # type: ignore
            case _:
                self.simple_id_response(id)

    def cancel_all_ids_except_newest(self) -> None:
        ids = [
            id["id"]
            for id in list(self.newest_requests.values())
            if id is not None
        ]
        for id in self.all_ids:
            if id in ids:
                continue
            self.simple_id_response(id)

        self.all_ids = []

    def handle_request(self, request: Request) -> None:
        command: str = request["command"]
        id: int = self.newest_ids[command]
        file: str = request["file"]
        result: (
            list[str | tuple[tuple[int, int], int, str]] | dict[str, str]
        ) = []
        cancelled: bool = False

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
                    full_text=self.files[file],
                    language=request["language"],  # type: ignore
                    text_range=request["text_range"],  # type: ignore
                )
                result += [token for token in pre_refined_result]  # type: ignore
            case "editorconfig":
                result = get_config(request["file_path"])  # type: ignore
            case "definition":
                result = get_definition(
                    self.files[file],
                    request["definition_starters"],  # type: ignore
                    request["current_word"],  # type: ignore
                )
            case _:
                cancelled = True

        response: Response = {
            "id": id,
            "type": "response",
            "cancelled": cancelled,
            "command": command,
            "result": result,
        }
        self.response_queue.put(response)
        self.newest_ids[command] = 0

    def run_tasks(self) -> None:
        while not self.requests_queue.empty():
            self.parse_line(self.requests_queue.get())

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
