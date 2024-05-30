from typing import NotRequired, TypedDict

COMMANDS: list[str] = ["autocomplete", "replacements", "highlight"]


class Message(TypedDict):
    """Base class for messages in and out of the server"""

    id: int
    type: str  # Can be "ping", "request", "response", "cancelled", "notification"


class Request(Message):
    """Request results/output from the server with command specific input"""

    command: str  # Can only be commands in COMMANDS
    file: str
    expected_keywords: NotRequired[list[str]]  # autocomplete, replacements
    current_word: NotRequired[str]  # autocomplete, replacements
    language: NotRequired[str]  # highlight


class Ping(Message):
    """Not really different from a standard Message but the Ping type allows for nice differentiation"""

    ...


class Notification(Message):
    """Notifies the server to add/update/remove a file for usage in fulfilling commands"""

    filename: str
    remove: bool
    contents: NotRequired[str]


class Response(Message):
    """Server responses to requests, notifications, and pings"""

    cancelled: bool
    command: NotRequired[str]
    result: NotRequired[list[str]]
