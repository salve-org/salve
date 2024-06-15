from re import Match, Pattern, compile
from unicodedata import category


def is_unicode_letter(char: str) -> bool:
    """Returns a boolean value of whether a given unicode char is a letter or not (includes "_" for code completion reasons)"""
    return char == "_" or category(char).startswith("L")


def find_words(full_text: str) -> list[str]:
    """Returns a list of all words in a given piece of text"""
    words_list = []
    current_word = ""

    for char in full_text:

        if is_unicode_letter(char):
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


def get_definition(
    full_text: str,
    definition_starters: list[tuple[str, str]],
    word_to_find: str,
) -> tuple[int, int, int]:
    """Finds all definitions of a given word in text using language definition starters"""
    default_pos = (0, 0, 0)  # line, column, length
    split_text: list[str] = full_text.splitlines()

    regex_possibilities: list[tuple[Pattern, str]] = [
        (
            (compile(definition[0] + word_to_find), definition[0])
            if definition[1] == "after"
            else (compile(word_to_find + definition[0]), definition[0])
        )
        for definition in definition_starters
    ]

    matches: list[tuple[Match, str, tuple[int, int]]] = []
    for regex, definition in regex_possibilities:
        start_pos: tuple[int, int] = (1, 0)

        while True:
            if start_pos[0] > len(split_text):
                break

            line: str = split_text[start_pos[0] - 1][start_pos[1] :]
            match_start: Match[str] | None = regex.search(line)

            if not match_start:
                start_pos = (start_pos[0] + 1, 0)
                continue

            matches.append((match_start, definition, start_pos))
            span = match_start.span()
            start_pos = (start_pos[0], start_pos[1] + span[0] + span[1])

    if not len(matches):
        return default_pos

    for best_match in matches:
        match_str: str = str(best_match[0].string)

        if word_to_find not in find_words(match_str):
            continue

        true_end: int = best_match[2][1] + best_match[0].span()[1]
        true_start: int = true_end - len(word_to_find)

        if match_str.startswith(word_to_find):
            true_start = 0
            true_end = len(word_to_find)

        if match_str.find(word_to_find) < true_start:
            true_start = match_str.find(word_to_find)
            true_end = true_start + len(word_to_find)

        word_found: str = str(best_match[0].string)[true_start:true_end]

        if word_found == word_to_find:
            return (best_match[2][0], true_start, len(word_to_find))

    return default_pos


# TESTS:

python_regexes: list[tuple[str, str]] = [
    (r"def ", "after"),
    (r"import .*,? ", "after"),
    (r"from ", "after"),
    (r"class ", "after"),
    (r":?.*=.*", "ahead"),
]
file = open("test2.py").read()

assert get_definition(
    file,
    python_regexes,
    "test",
) == (10, 6, 4)

assert get_definition(
    file,
    python_regexes,
    "example",
) == (3, 0, 7)

assert get_definition(
    file,
    python_regexes,
    "re",
) == (1, 5, 2)

assert get_definition(
    file,
    python_regexes,
    "x",
) == (5, 3, 1)

assert get_definition(
    file,
    [("", "ahead")],
    "x",
) == (5, 3, 1)

assert get_definition(
    file,
    [("", "ahead")],
    "test",
) == (8, 0, 4)
