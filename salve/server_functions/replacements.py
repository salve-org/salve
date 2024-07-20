from difflib import get_close_matches

from .misc import find_words


def get_replacements(
    full_text: str, expected_keywords: list[str], replaceable_word: str
) -> list[str]:
    """Returns a list of possible and plausible replacements for a given word"""
    # Get all words in file
    starter_words: list[str] = find_words(full_text)
    starter_words.extend(
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
