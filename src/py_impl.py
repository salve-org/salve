from argparse import ArgumentParser
from json import load
from json.decoder import JSONDecodeError
from sys import exit
from unicodedata import category

__version__ = "0.1.0"


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
        words_after_original_removal = expected_keywords

    relevant_words = [
        word for word in words_after_original_removal if word.startswith(original_word)
    ]

    autocomplete_matches = sorted(
        set(relevant_words), key=(lambda s: (-relevant_words.count(s), len(s), s))
    )

    return autocomplete_matches


if __name__ == "__main__":
    parser = ArgumentParser(
        prog="MakeshiftLSP",
        description="A makeshift LSP for the DIP editor that gives autocompletions",
    )

    parser.add_argument(
        "--version", action="version", version="%(prog)s " + __version__
    )
    parser.add_argument(
        "input_file",
        type=str,
        help="Expected keywords, full text, and the original word in a JSON file",
    )

    args = parser.parse_args()

    try:
        with open(args.input_file) as file:
            data: dict = load(file)
    except JSONDecodeError or FileNotFoundError:
        print("Input data is not valid JSON or file does not exist")
        exit(1)

    try:
        keywords = data["keywords"]
        full_text = data["full_text"]
        original_word = data["original_word"]
    except KeyError as e:
        error_str = f"Item {e} could not be read properly"
        if not data.__contains__(e):
            error_str = f"Input JSON lacks {e}"
        print(error_str)
        exit(1)

    print(
        find_autocompletions(data["keywords"], data["full_text"], data["original_word"])
    )
