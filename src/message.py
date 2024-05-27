from typing import NotRequired, TypedDict


class Message(TypedDict):
    id: int
    type: str  # Can be "ping", "request", "response", "cancelled", "notification"


class Request(Message):
    command: str  # Currently can only be "autocopmlete"
    expected_keywords: list[str]
    full_text: str
    current_word: str


class Ping(Message): ...


class Notification(Message):
    filename: str
    remove: bool
    diff: NotRequired[str]


class Response(Message):
    cancelled: bool
    result: NotRequired[list[str]]
