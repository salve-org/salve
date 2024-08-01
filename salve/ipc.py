from logging import Logger, getLogger
from multiprocessing import Process, Queue, freeze_support
from pathlib import Path
from random import randint

from .misc import (
    COMMAND,
    COMMANDS,
    EDITORCONFIG,
    Notification,
    Request,
    RequestQueueType,
    Response,
    ResponseQueueType,
)
from .server import Server

# from collegamento import FileClient



class IPC:
    """The IPC class is used to talk to the server and run commands. The public API includes the following methods:
    - IPC.request()
    - IPC.cancel_request()
    - IPC.update_file()
    - IPC.remove_file()
    - IPC.kill_IPC()
    """

    def __init__(self, id_max: int = 15_000) -> None:
        self.all_ids: list[int] = []
        self.id_max = id_max
        self.current_ids: dict[str, int] = {}
        self.newest_responses: dict[str, Response | None] = {}
        for command in COMMANDS:
            self.current_ids[command] = 0
            self.newest_responses[command] = None

        self.files: dict[str, str] = {}

        self.logger: Logger = getLogger("IPC")
        self.logger.info("Creating server")
        self.response_queue: ResponseQueueType = Queue()
        self.requests_queue: RequestQueueType = Queue()
        self.main_server: Process
        self.create_server()
        self.logger.info("Initialization is complete")

    def create_server(self) -> None:
        """Creates the main_server through a subprocess - internal API"""
        freeze_support()
        server_logger = getLogger("Server")
        self.main_server = Process(
            target=Server,
            args=(self.response_queue, self.requests_queue, server_logger),
            daemon=True,
        )
        self.main_server.start()
        self.logger.info("Server created")

        self.logger.info("Copying files to server")
        files_copy = self.files.copy()
        self.files = {}
        for file, data in files_copy.items():
            self.update_file(file, data)
        self.logger.debug("Finished copying files to server")

    def create_message(self, type: str, **kwargs) -> None:
        """Creates a Message based on the args and kwawrgs provided. Highly flexible. - internal API"""
        self.logger.info("Creating message for server")
        id = randint(1, self.id_max)  # 0 is reserved for the empty case
        while id in self.all_ids:
            id = randint(1, self.id_max)
        self.all_ids.append(id)

        self.logger.debug("ID for message created")
        if not self.main_server.is_alive():
            self.logger.critical(
                "Server was killed at some point, creating server"
            )
            self.create_server()

        match type:
            case "request":
                self.logger.info("Creating request for server")
                command = kwargs.get("command", "")
                self.current_ids[command] = id
                request: Request = {
                    "id": id,
                    "type": type,
                    "command": command,
                    "file": "",
                }
                request.update(**kwargs)
                self.logger.debug(f"Request created: {request}")
                self.requests_queue.put(request)
                self.logger.info("Message sent")
            case "notification":
                self.logger.info("Creating notification for server")
                notification: Notification = {
                    "id": id,
                    "type": type,
                    "remove": False,
                    "file": "",
                    "contents": "",
                }
                notification.update(**kwargs)
                self.logger.debug(f"Notification created: {notification}")
                self.requests_queue.put(notification)
                self.logger.info("Message sent")

    def request(
        self,
        command: COMMAND,
        file: str = "",
        expected_keywords: list[str] = [""],
        current_word: str = "",
        language: str = "Text",
        text_range: tuple[int, int] = (1, -1),
        file_path: Path | str = Path(__file__),
        definition_starters: list[tuple[str, str]] = [("", "before")],
    ) -> None:
        """Sends the main_server a request of type command with given kwargs - external API"""
        self.logger.debug("Beginning request")
        if command not in COMMANDS:
            self.logger.exception(
                f"Command {command} not in builtin commands. Those are {COMMANDS}!"
            )
            raise Exception(
                f"Command {command} not in builtin commands. Those are {COMMANDS}!"
            )

        if file not in self.files and command != EDITORCONFIG:
            self.logger.exception(f"File {file} does not exist in system!")
            raise Exception(f"File {file} does not exist in system!")

        self.logger.debug("Sending info to create_message()")
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

    def cancel_request(self, command: str) -> None:
        """Cancels a request of type command - external API"""
        if command not in COMMANDS:
            self.logger.exception(
                f"Cannot cancel command {command}, valid commands are {COMMANDS}"
            )
            raise Exception(
                f"Cannot cancel command {command}, valid commands are {COMMANDS}"
            )

        self.logger.info(f"Cancelled command: {command}")
        self.current_ids[command] = 0

    def parse_response(self, res: Response) -> None:
        """Parses main_server output line and discards useless responses - internal API"""
        self.logger.debug("Parsing server response")
        id = res["id"]
        self.all_ids.remove(id)

        if "command" not in res:
            self.logger.info("Response was notification response")
            return

        command = res["command"]
        if id != self.current_ids[command]:
            self.logger.info("Response is from old request")
            return

        self.logger.info(f"Response is useful for command type: {command}")
        self.current_ids[command] = 0
        self.newest_responses[command] = res

    def check_responses(self) -> None:
        """Checks all main_server output by calling IPC.parse_line() on each response - internal API"""
        self.logger.debug("Checking responses")
        while not self.response_queue.empty():
            self.parse_response(self.response_queue.get())

    def get_response(self, command: str) -> Response | None:
        """Checks responses and returns the current response of type command if it has been returned - external API"""
        self.logger.info(f"Getting response for type: {command}")
        if command not in COMMANDS:
            self.logger.exception(
                f"Cannot get response of command {command}, valid commands are {COMMANDS}"
            )
            raise Exception(
                f"Cannot get response of command {command}, valid commands are {COMMANDS}"
            )

        self.check_responses()
        response: Response | None = self.newest_responses[command]
        self.newest_responses[command] = None
        self.logger.info("Response retrieved")
        return response

    def update_file(self, file: str, current_state: str) -> None:
        """Updates files in the system - external API"""

        self.logger.info(f"Updating file: {file}")
        self.files[file] = current_state

        self.logger.debug("Notifying server of file update")
        self.create_message("notification", file=file, contents=current_state)

    def remove_file(self, file: str) -> None:
        """Removes a file from the main_server - external API"""
        if file not in list(self.files.keys()):
            self.logger.exception(
                f"Cannot remove file {file} as file is not in file database!"
            )
            raise Exception(
                f"Cannot remove file {file} as file is not in file database!"
            )

        self.logger.info("Notifying server of file deletion")
        self.create_message("notification", remove=True, file=file)

    def kill_IPC(self) -> None:
        """Kills the main_server when salve_ipc's services are no longer required - external API"""
        self.logger.info("Killing server")
        self.main_server.kill()
