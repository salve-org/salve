from difflib import restore, get_close_matches
from json import dumps, loads
from os import set_blocking
from selectors import EVENT_READ, DefaultSelector
from sys import exit, stderr, stdin, stdout
from time import time
from unicodedata import category

from message import Request, Message, Response


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
    full_text: str, expected_keywords: list[str], current_word: str
) -> list[str]:
    """Returns a list of autocompletions based on the word"""

    words_in_text: list[str] = find_words(full_text)

    words_after_original_removal = [
        word for word in words_in_text if word != current_word
    ]

    no_usable_words_in_text: bool = not words_after_original_removal
    if no_usable_words_in_text:
        words_after_original_removal += expected_keywords

    relevant_words = [
        word for word in words_after_original_removal if word.startswith(current_word)
    ]

    autocomplete_matches = sorted(
        set(relevant_words), key=(lambda s: (-relevant_words.count(s), len(s), s))
    )

    return autocomplete_matches


def get_replacements(
    full_text: str, expected_keywords: list[str], replaceable_word: str
) -> list[str]:
    # Get all words in file
    starter_words = find_words(full_text)
    starter_words += (
        expected_keywords * 3
    )  # We add a multiplier of three to boost the score of keywords
    while replaceable_word in starter_words:
        starter_words.remove(replaceable_word)

    # Get close matches
    starters_no_duplicates = set(starter_words)
    similar_words = get_close_matches(
        replaceable_word,
        starters_no_duplicates,
        n=len(starters_no_duplicates),
        cutoff=0.6,
    )

    # Reintroduce duplicates
    similar_with_duplicates = [word for word in starter_words if word in similar_words]

    ranked_matches = sorted(
        set(similar_with_duplicates),
        key=(lambda s: (-similar_with_duplicates.count(s), len(s), s)),
    )

    return ranked_matches


class Handler:
    def __init__(self) -> None:
        set_blocking(stdin.fileno(), False)
        set_blocking(stdout.fileno(), False)
        self.selector = DefaultSelector()
        self.selector.register(stdin, EVENT_READ)

        self.id_list: list[int] = []
        self.newest_request: Request | None = None
        self.commands: list[str] = ["autocomplete"]
        self.newest_ids: dict[str, int] = {}
        self.newest_requests: dict[str, Request | None] = {}
        for command in self.commands:
            self.newest_ids[command] = 0
            self.newest_requests[command] = None

        self.files: dict[str, str] = {}

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
        match json_input["type"]:
            case "ping":
                self.cancel_id(id)
            case "notification":
                filename: str = json_input["filename"]  # type: ignore
                if json_input["remove"]:  # type: ignore
                    self.files.pop(filename)
                    return
                diff: list[str] = json_input["diff"].splitlines()  # type: ignore
                self.files[filename] = "".join(restore(diff, 2))  # type: ignore
            case _:
                self.id_list.append(id)
                command: str = json_input["command"] # type: ignore
                self.newest_ids[command] = id
                self.newest_request = json_input  # type: ignore
                self.newest_requests[command] = json_input # type: ignore

    def cancel_all_ids_except_newest(self) -> None:
        for id in self.id_list:
            if id in list(self.newest_ids.values()):
                continue
            self.cancel_id(id)

    def handle_request(self, request: Request) -> None:
        file: str = request["file"]
        result: list[str] = [""]
        match request["command"]:
            case "autocomplete":
                result: list[str] = []
                if file in self.files:
                    result = find_autocompletions(
                        full_text=self.files[file],
                        expected_keywords=["expected_keywords"],
                        current_word=request["current_word"],
                    )
            case "replacements":
                if file in self.files:
                    result = get_replacements(
                        full_text=self.files[file],
                        expected_keywords=["expected_keywords"],
                        replaceable_word=request["current_word"],
                    )

        command: str = request["command"]
        response: Response = {
            "id": request["id"],
            "type": "response",
            "cancelled": False,
            "command": command,
            "result": result,
        }
        self.write_response(response)
        self.newest_ids[command] = 0

    def run_tasks(self) -> None:
        current_time = time()
        if current_time - self.old_time > 5:
            exit(0)

        events = self.selector.select(0.025)
        if not events:
            return

        for line in stdin:
            # Prevent zombie process
            if self.old_time != current_time:
                self.old_time = current_time

            self.parse_line(line)

        self.cancel_all_ids_except_newest()

        if not self.newest_request:  # There may have only been refreshes
            return

        if not list(self.newest_requests.values()): # There may have only been refreshes
            return

        # Actual work
        request = self.newest_request
        for requesty in list(self.newest_requests.values()):
            print(requesty, file=stderr)
            pass
        self.handle_request(request)

        self.id_list = []
        self.newest_request = None
        command: str = request["command"]
        self.newest_requests[command] = None


if __name__ == "__main__":
    handler = Handler()
    while True:
        handler.run_tasks()
