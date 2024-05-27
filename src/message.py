from typing import NotRequired, TypedDict


class Message(TypedDict):
    id: int
    type: str  # Can be "ping", "request", "response", "cancelled", "notification"


class AutocompleteRequest(Message):
    form: str  # Currently can only be "autocopmlete"
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
    autocomplete: NotRequired[list[str]]
