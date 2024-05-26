from typing import TypedDict, NotRequired


class Message(TypedDict):
    id: int
    type: str  # Can be "ping", "request", "response", "cancelled"


class Request(Message):
    form: str  # Currently can only be "autocopmlete"
    expected_keywords: list[str]
    full_text: str
    current_word: str


class Ping(Message): ...


class Response(Message):
    cancelled: bool
    autocomplete: NotRequired[list[str]]
