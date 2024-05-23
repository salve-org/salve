from typing import TypedDict, NotRequired


class ResReq(TypedDict):
    id: int
    type: str  # "cancelled", "response", "refresh", "request"
    index: NotRequired[str]  # Unfiltered input string
    item: NotRequired[str]
