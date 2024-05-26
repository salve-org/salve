from json import dumps, loads
from sys import exit, stdin, stdout
from os import set_blocking
from time import time
from typing import TypedDict, NotRequired
from selectors import EVENT_READ, DefaultSelector


class ResReq(TypedDict):
    id: int
    type: str  # "cancelled", "response", "refresh", "request"
    index: NotRequired[str]  # Only in "request"
    item: NotRequired[str]  # Only in "response"


class RequestHandler:
    def __init__(self):
        set_blocking(stdin.fileno(), False)
        set_blocking(stdout.fileno(), False)
        self.selector = DefaultSelector()
        self.selector.register(stdin, EVENT_READ)

        self.id_list = []
        self.newest_request = None
        self.newest_id = 0

        self.old_time = time()

        self.random_list = ["apples", "oranges", "bananas"]

    def get_item(self, index: str) -> str:
        try:
            intdex = int(index)
        except ValueError:
            return "?"
        try:
            return self.random_list[intdex]
        except IndexError:
            return "?"

    def write_resreq(self, response: ResReq) -> None:
        stdout.write(dumps(response) + "\n")
        stdout.flush()

    def parse_line(self, line: str) -> None:
        json_input: ResReq = loads(line)
        id: int = json_input["id"]
        if json_input["type"] == "refresh":
            self.write_resreq({"id": id, "type": "response"})
            return
        self.id_list.append(id)
        self.newest_id = id
        self.newest_request = json_input

    def cancel_all_ids_except_newest(self) -> None:
        for id in self.id_list:
            if id == self.newest_id:
                continue
            self.write_resreq({"id": id, "type": "cancelled"})

    def run_tasks(self):
        current_time = time()
        if current_time - self.old_time > 5:
            exit(0)

        events = self.selector.select(0.025)
        if not events:
            return

        self.old_time = current_time
        for line in stdin:
            self.parse_line(line)

        self.cancel_all_ids_except_newest()

        if not self.newest_request:  # There may have only been refreshes
            return

        index_request: str = self.newest_request["index"]  # type: ignore

        self.write_resreq(
            {
                "id": self.newest_id,
                "type": "response",
                "item": self.get_item(index_request),
            }
        )

        self.id_list = []
        self.newest_request = None
        self.newest_id = 0


if __name__ == "__main__":
    handler = RequestHandler()
    while True:
        handler.run_tasks()
