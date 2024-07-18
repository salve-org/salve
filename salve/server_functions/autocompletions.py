from .misc import find_words


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
        relevant_words.extend(
            expected_keywords * 3
        )  # We add a multiplier of three to boost the score of keywords

    relevant_words = [
        word for word in relevant_words if word.startswith(current_word)
    ]

    autocomplete_matches = sorted(
        set(relevant_words),
        key=(lambda s: (-relevant_words.count(s), len(s), s)),
    )

    return autocomplete_matches
