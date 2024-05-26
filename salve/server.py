from json import loads, dumps
from sys import exit
from unicodedata import category
from os import set_blocking
from sys import stdin, stdout
from message import Message, Request, Response
from selectors import EVENT_READ, DefaultSelector
from time import time


def find_words(full_text: str) -> list[str]:
    words_list = []
    current_word = ""

    for char in full_text:

        is_unicode_letter: bool = char == "_" or category(char).startswith("L")
        if is_unicode_letter:
            current_word += char
            continue

        word_is_empty: bool = not current_word
        if word_is_empty:
            continue

        words_list.append(current_word)
        current_word = ""

    word_left = bool(current_word)
    if word_left:
        words_list.append(current_word)

    return words_list


def find_autocompletions(
    expected_keywords: list[str], full_text: str, original_word: str
) -> list[str]:
    """Returns a list of autocompletions based on the word"""

    words_in_text: list[str] = find_words(full_text)

    words_after_original_removal = [
        word for word in words_in_text if word != original_word
    ]

    no_usable_words_in_text: bool = not words_after_original_removal
    if no_usable_words_in_text:
        words_after_original_removal += expected_keywords

    relevant_words = [
        word for word in words_after_original_removal if word.startswith(original_word)
    ]

    autocomplete_matches = sorted(
        set(relevant_words), key=(lambda s: (-relevant_words.count(s), len(s), s))
    )

    return autocomplete_matches


class Handler:
    def __init__(self) -> None:
        set_blocking(stdin.fileno(), False)
        set_blocking(stdout.fileno(), False)
        self.selector = DefaultSelector()
        self.selector.register(stdin, EVENT_READ)

        self.id_list: list[int] = []
        self.newest_request: Request | None = None
        self.newest_id: int = 0

        self.old_time = time()

    def write_response(self, response: Response) -> None:
        stdout.write(dumps(response) + "\n")
        stdout.flush()

    def cancel_id(self, id: int) -> None:
        response: Response = {"id": id, "type": "response", "cancelled": True}
        self.write_response(response)

    def parse_line(self, line: str) -> None:
        json_input: Message = loads(line)
        id: int = json_input["id"]
        if json_input["type"] == "ping":
            self.cancel_id(id)
            return
        self.id_list.append(id)
        self.newest_id = id
        self.newest_request = json_input  # type: ignore

    def cancel_all_ids_except_newest(self) -> None:
        for id in self.id_list:
            if id == self.newest_id:
                continue
            self.cancel_id(id)

    def run_tasks(self) -> None:
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

        # Actual work
        autocomplete = find_autocompletions(
            self.newest_request["expected_keywords"],
            self.newest_request["full_text"],
            self.newest_request["current_word"],
        )

        response: Response = {
            "id": self.newest_request["id"],
            "type": "response",
            "cancelled": False,
            "autocomplete": autocomplete,
        }
        self.write_response(response)

        self.id_list = []
        self.newest_request = None
        self.newest_id = 0


if __name__ == "__main__":
    handler = Handler()
    while True:
        handler.run_tasks()
