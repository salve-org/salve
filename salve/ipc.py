from pathlib import Path

from collegamento import FileClient

from .misc import (
    AUTOCOMPLETE,
    COMMAND,
    COMMANDS,
    DEFINITION,
    EDITORCONFIG,
    HIGHLIGHT,
    LINKS_AND_CHARS,
    REPLACEMENTS,
)
from .wrappers import (
    editorconfig_request_wrapper,
    find_autocompletions_request_wrapper,
    get_definition_request_wrapper,
    get_highlights_request_wrapper,
    get_replacements_request_wrapper,
    get_special_tokens_request_wrapper,
)


class IPC(FileClient):
    """The IPC class is used to talk to the server and run commands. The public API includes the following methods:
    - IPC.request()
    - IPC.update_file()
    - IPC.remove_file()
    - IPC.kill_IPC()
    """

    def __init__(self, id_max: int = 15000) -> None:
        super().__init__(
            id_max=id_max,
            commands={
                AUTOCOMPLETE: find_autocompletions_request_wrapper,
                REPLACEMENTS: get_replacements_request_wrapper,
                HIGHLIGHT: get_highlights_request_wrapper,
                EDITORCONFIG: editorconfig_request_wrapper,
                DEFINITION: get_definition_request_wrapper,
                LINKS_AND_CHARS: get_special_tokens_request_wrapper,
            },
        )

    # Pyright likes to complain and say this won't work but it actually does
    # TODO: Use plum or custom multiple dispatch (make it a new project for salve organization)
    def request(  # type: ignore
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
        request: dict = {
            "command": command,
            "expected_keywords": expected_keywords,
            "current_word": current_word,
            "language": language,
            "text_range": text_range,
            "file_path": file_path,
            "definition_starters": definition_starters,
        }
        if file:
            request.update({"file": file})
        super().request(request)
