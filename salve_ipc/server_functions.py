from difflib import get_close_matches
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


def find_autocompletions(
    full_text: str, expected_keywords: list[str], current_word: str
) -> list[str]:
    """Returns a list of autocompletions based on the word, text, and language keywords"""

    words_in_text: list[str] = find_words(full_text)

    words_after_original_removal = [
        word for word in words_in_text if word != current_word
    ]

    relevant_words = [
        word
        for word in words_after_original_removal
        if word.startswith(current_word)
    ]

    no_usable_words_in_text: bool = not relevant_words
    if no_usable_words_in_text:
        relevant_words += expected_keywords

    relevant_words = [
        word for word in relevant_words if word.startswith(current_word)
    ]

    autocomplete_matches = sorted(
        set(relevant_words),
        key=(lambda s: (-relevant_words.count(s), len(s), s)),
    )

    return autocomplete_matches


def get_replacements(
    full_text: str, expected_keywords: list[str], replaceable_word: str
) -> list[str]:
    """Returns a list of possible and plausible replacements for a given word"""
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
    similar_with_duplicates = [
        word for word in starter_words if word in similar_words
    ]

    ranked_matches = sorted(
        set(similar_with_duplicates),
        key=(lambda s: (-similar_with_duplicates.count(s), len(s), s)),
    )

    return ranked_matches
