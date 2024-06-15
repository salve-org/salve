from multiprocessing import Pipe, Process, Queue, freeze_support
from multiprocessing.connection import Connection
from multiprocessing.queues import Queue as GenericClassQueue
from pathlib import Path
from random import randint

from beartype import beartype

from .misc import COMMANDS, Notification, Request, Response
from .server import Server


class IPC:
    """The IPC class is used to talk to the server and run commands ("autocomplete", "replacements", and "highlight"). The public API includes the following methods:
    - IPC.request()
    - IPC.cancel_request()
    - IPC.update_file()
    - IPC.remove_file()
    - IPC.kill_IPC()
    """

    @beartype
    def __init__(self, id_max: int = 15_000) -> None:
        self.all_ids: list[int] = []
        self.id_max = id_max
        self.current_ids: dict[str, int] = {}
        self.newest_responses: dict[str, Response | None] = {}
        for command in COMMANDS:
            self.current_ids[command] = 0
            self.newest_responses[command] = None

        self.files: dict[str, str] = {}

        self.response_queue: GenericClassQueue[Response] = Queue()
        self.requests_queue: GenericClassQueue[Request | Notification] = (
            Queue()
        )
        self.client_end: Connection
        self.main_server: Process
        self.create_server()

    def create_server(self) -> None:
        """Creates the main_server through a subprocess - internal API"""
        self.client_end, server_end = Pipe()
        freeze_support()
        self.main_server = Process(
            target=Server,
            args=(server_end, self.response_queue, self.requests_queue),
            daemon=True,
        )
        self.main_server.start()

        files_copy = self.files.copy()
        self.files = {}
        for filename, data in files_copy.items():
            self.update_file(filename, data)

    @beartype
    def create_message(self, type: str, **kwargs) -> None:
        """Creates a Message based on the args and kwawrgs provided. Highly flexible. - internal API"""
        id = randint(1, self.id_max)  # 0 is reserved for the empty case
        while id in self.all_ids:
            id = randint(1, self.id_max)
        self.all_ids.append(id)

        if not self.main_server.is_alive():
            self.create_server()

        match type:
            case "request":
                command = kwargs.get("command", "")
                self.current_ids[command] = id
                request: Request = {
                    "id": id,
                    "type": type,
                    "command": command,
                    "file": kwargs.get("file", ""),
                    "expected_keywords": kwargs.get("expected_keywords", []),
                    "current_word": kwargs.get("current_word", ""),
                    "language": kwargs.get("language", ""),
                    "text_range": kwargs.get("text_range", (1, -1)),
                    "file_path": kwargs.get("file_path", __file__),
                    "definition_starters": kwargs.get(
                        "definition_starters", [("", "ahead")]
                    ),
                }
                self.requests_queue.put(request)
            case "notification":
                notification: Notification = {
                    "id": id,
                    "type": type,
                    "remove": kwargs.get("remove", False),
                    "file": kwargs.get("filename", ""),
                    "contents": kwargs.get("contents", ""),
                }
                self.requests_queue.put(notification)

    @beartype
    def request(
        self,
        command: str,
        file: str,
        expected_keywords: list[str] = [""],
        current_word: str = "",
        language: str = "Text",
        text_range: tuple[int, int] = (1, -1),
        file_path: Path | str = Path(__file__),
        definition_starters: list[tuple[str, str]] = [("", "ahead")],
    ) -> None:
        """Sends the main_server a request of type command with given kwargs - external API"""
        if command not in COMMANDS:
            self.kill_IPC()
            raise Exception(
                f"Command {command} not in builtin commands. Those are {COMMANDS}!"
            )

        if file not in self.files:
            self.kill_IPC()
            raise Exception(f"File {file} does not exist in system!")

        self.create_message(
            type="request",
            command=command,
            file=file,
            expected_keywords=expected_keywords,
            current_word=current_word,
            language=language,
            text_range=text_range,
            file_path=file_path,
            definition_starters=definition_starters,
        )

    @beartype
    def cancel_request(self, command: str):
        """Cancels a request of type command - external API"""
        if command not in COMMANDS:
            self.kill_IPC()
            raise Exception(
                f"Cannot cancel command {command}, valid commands are {COMMANDS}"
            )

        self.current_ids[command] = 0

    @beartype
    def parse_response(self, res: Response) -> None:
        """Parses main_server output line and discards useless responses - internal API"""
        id = res["id"]
        self.all_ids.remove(id)

        if "command" not in res:
            return

        command = res["command"]
        if id != self.current_ids[command]:
            return

        self.current_ids[command] = 0
        self.newest_responses[command] = res

    def check_responses(self) -> None:
        """Checks all main_server output by calling IPC.parse_line() on each response - internal API"""
        while not self.response_queue.empty():
            self.parse_response(self.response_queue.get())

    @beartype
    def get_response(self, command: str) -> Response | None:
        """Runs IPC.check_responses() and returns the current response of type command if it has been returned - external API"""
        if command not in COMMANDS:
            self.kill_IPC()
            raise Exception(
                f"Cannot get response of command {command}, valid commands are {COMMANDS}"
            )

        self.check_responses()
        response: Response | None = self.newest_responses[command]
        self.newest_responses[command] = None
        return response

    @beartype
    def update_file(self, filename: str, current_state: str) -> None:
        """Updates files in the system - external API"""

        self.files[filename] = current_state

        self.create_message(
            "notification", filename=filename, contents=current_state
        )

    @beartype
    def remove_file(self, filename: str) -> None:
        """Removes a file from the main_server - external API"""
        if filename not in list(self.files.keys()):
            self.kill_IPC()
            raise Exception(
                f"Cannot remove file {filename} as file is not in file database!"
            )

        self.create_message("notification", remove=True, filename=filename)

    def kill_IPC(self) -> None:
        """Kills the main_server when salve_ipc's services are no longer required - external API"""
        self.main_server.kill()
