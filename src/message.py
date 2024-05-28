from typing import NotRequired, TypedDict


class Message(TypedDict):
    id: int
    type: str  # Can be "ping", "request", "response", "cancelled", "notification"


class Request(Message):
    command: str  # Currently can only be "autocopmlete"
    expected_keywords: list[str]
    file: str
    current_word: str


class Ping(Message): ...


class Notification(Message):
    filename: str
    remove: bool
    diff: NotRequired[str]


class Response(Message):
    cancelled: bool
    command: NotRequired[str]
    result: NotRequired[list[str]]
