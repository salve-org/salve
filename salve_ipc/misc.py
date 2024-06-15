from pathlib import Path
from typing import NotRequired, TypedDict

COMMANDS: list[str] = [
    "autocomplete",
    "replacements",
    "highlight",
    "editorconfig",
    "definition",
]


class Message(TypedDict):
    """Base class for messages in and out of the server"""

    id: int
    type: str  # Can be "request", "response", "notification"


class Request(Message):
    """Request results/output from the server with command specific input"""

    command: str  # Can only be commands in COMMANDS
    file: str
    expected_keywords: NotRequired[list[str]]  # autocomplete, replacements
    current_word: NotRequired[str]  # autocomplete, replacements, definition
    language: NotRequired[str]  # highlight
    text_range: NotRequired[tuple[int, int]]  # highlight
    file_path: NotRequired[Path | str]  # editorconfig
    definition_starters: NotRequired[
        list[tuple[str, str]]
    ]  # definition (list of regexes)


class Notification(Message):
    """Notifies the server to add/update/remove a file for usage in fulfilling commands"""

    file: str
    remove: bool
    contents: NotRequired[str]


class Response(Message):
    """Server responses to requests and notifications"""

    cancelled: bool
    command: NotRequired[str]
    result: NotRequired[
        list[str | tuple[tuple[int, int], int, str]] | dict[str, str]
    ]
