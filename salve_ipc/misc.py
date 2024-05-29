from typing import NotRequired, TypedDict

COMMANDS: list[str] = ["autocomplete", "replacements", "highlight"]


class Message(TypedDict):
    id: int
    type: str  # Can be "ping", "request", "response", "cancelled", "notification"


class Request(Message):
    command: str  # Can only be commands in COMMANDS
    file: str
    expected_keywords: NotRequired[list[str]]
    current_word: NotRequired[str]
    language: NotRequired[str]


class Ping(Message): ...


class Notification(Message):
    filename: str
    remove: bool
    diff: NotRequired[str]


class Response(Message):
    cancelled: bool
    command: NotRequired[str]
    result: NotRequired[list[str]]
