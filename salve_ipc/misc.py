from pathlib import Path
from typing import NotRequired, TypedDict

COMMANDS: list[str] = [
    "autocomplete",
    "replacements",
    "highlight",
    "editorconfig",
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
    current_word: NotRequired[str]  # autocomplete, replacements
    language: NotRequired[str]  # highlight
    text_range: NotRequired[tuple[int, int]]
    file_path: NotRequired[Path]  # editorconfig


class Notification(Message):
    """Notifies the server to add/update/remove a file for usage in fulfilling commands"""

    file: str
    remove: bool
    contents: NotRequired[str]


class Response(Message):
    """Server responses to requests and notifications"""

    cancelled: bool
    command: NotRequired[str]
    result: NotRequired[list[str | tuple[tuple[int, int], int, str]]]
