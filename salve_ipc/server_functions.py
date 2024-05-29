from dataclasses import dataclass
from difflib import get_close_matches
from unicodedata import category

from pygments import lex
from pygments.lexer import Lexer
from pygments.lexers import get_lexer_by_name
from pygments.token import _TokenType

default_tokens: list[str] = [
    "Token.Text" "Token.Text.Whitespace",
    "Token.Error",
    "Token.Keyword",
    "Token.Name",
    "Token.Literal.String",
    "Token.Literal.Number",
    "Token.Literal",
    "Token.Operator",
    "Token.Punctuation",
    "Token.Comment",
    "Token.Generic",
]
generic_tokens: list[str] = [
    "Text",
    "Whitespace",
    "Error",
    "Keyword",
    "Name",
    "String",
    "Number",
    "Literal",
    "Operator",
    "Punctuation",
    "Comment",
    "Generic",
]


@dataclass
class Token:
    start_index: tuple[int, int]  # line, pos
    token_length: int
    highlight_type: str


def get_new_token(old_token: str) -> str:
    new_type: str = generic_tokens[0]
    for index, token in enumerate(default_tokens):
        if token.startswith(old_token):
            new_type = generic_tokens[index]
            break
    return new_type


def get_highlights(full_text: str, language: str = "text") -> list:
    lexer: Lexer = get_lexer_by_name(language)
    new_tokens: list[Token] = []
    og_tokens: list[tuple[_TokenType, str]] = list(lex(full_text, lexer))
    start_index: tuple[int, int] = (1, 0)

    for token in og_tokens:
        new_type: str = get_new_token(str(token[0]))
        token_str: str = token[1]
        token_len: int = len(token_str)
        new_token = Token(start_index, token_len, new_type)
        new_tokens.append(new_token)

        if token_str == "\n":
            start_index = (start_index[0] + 1, 0)
            continue

        start_index = (start_index[0], start_index[1] + token_len)

    return new_tokens


def is_unicode_letter(char: str) -> bool:
    return char == "_" or category(char).startswith("L")


def find_words(full_text: str) -> list[str]:
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
