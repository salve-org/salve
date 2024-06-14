from re import Match, Pattern, compile


def get_definition(
    full_text: str,
    definition_starters: list[tuple[str, str]],
    word_to_find: str,
) -> tuple[int, int, int]:
    # line, column, length
    default_pos = (0, 0, 0)
    regex_possibilities: list[tuple[Pattern, str]] = [
        (
            (compile(definition[0] + word_to_find), definition[0])
            if definition[1] == "after"
            else (compile(word_to_find + definition[0]), definition[0])
        )
        for definition in definition_starters
    ]
    split_text: list[str] = full_text.splitlines()
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

    best_match = matches[0]
    match_str: str = str(best_match[0].string)
    true_end: int = best_match[2][1] + best_match[0].span()[1]
    true_start: int = true_end - len(word_to_find)
    if match_str.startswith(word_to_find):
        true_start = 0
        true_end = len(word_to_find)
    return (best_match[2][0], true_start, len(word_to_find))


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
) == (6, 6, 4)

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
