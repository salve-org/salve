from functools import cache
from unicodedata import category


@cache
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
