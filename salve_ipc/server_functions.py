from difflib import get_close_matches
from unicodedata import category
from re import Match, Pattern, compile

from pygments import lex
from pygments.lexer import Lexer
from pygments.lexers import get_lexer_by_name
from pygments.token import _TokenType

default_tokens: list[str] = [
    "Token.Text.Whitespace",
    "Token.Text",
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
    "Whitespace",
    "Text",
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
    "Link",  # Website link (Not given by pygments)
    "Hidden_Char",  # Hidden chars (no width space kind of stuff)
]

Token = tuple[tuple[int, int], int, str]


def get_new_token_type(old_token: str) -> str:
    """Turns pygments token types into a generic predefined Token"""
    new_type: str = generic_tokens[0]
    for index, token in enumerate(default_tokens):
        if old_token.startswith(token):
            new_type = generic_tokens[index]
            break
    return new_type


url_regex: Pattern = compile(r"(ftp|http|https):\/\/[a-zA-Z0-9_-]")


def get_urls(lines: list[str], start_line: int = 1) -> list[Token]:
    start_pos: tuple[int, int] = (start_line, 0)
    url_toks: list[Token] = []
    while True:
        if start_pos[0] >= len(lines) + start_line:
            break
        line: str = lines[start_pos[0] - start_line][start_pos[1] :]
        match_start: Match[str] | None = url_regex.search(line)
        if match_start is None:
            if start_pos[0] >= len(lines) + start_line:
                break
            start_pos = (start_pos[0] + 1, 0)
            continue
        token_start_col = match_start.span()[0]  # type: ignore
        url: str = line[token_start_col:]

        # Narrow down the url
        url = url.strip()
        url = url.split()[0]
        url = url.split("'")[0]
        url = url.split("`")[0]
        url = url.split('"')[0]
        url = url.rstrip(".,?!")
        if "(" not in url:  # urls can contain spaces (e.g. wikipedia)
            url = url.rstrip(")")
        url = url.rstrip(".,?!")

        url_len: int = len(url)
        token: Token = ((start_pos[0], token_start_col), url_len, "Link")
        url_toks.append(token)
        start_pos = (start_pos[0], start_pos[1] + url_len + token_start_col)

    return url_toks


hidden_chars: dict[str, str] = {
    "\u00a0": "Non-breaking space",
    "\u180e": "Control char (Mongolian vowel separator)",
    "\u2000": "Control char (en quad)",
    "\u2001": "Control char (em quad)",
    "\u2002": "Control char (en space)",
    "\u2003": "Control char (em space)",
    "\u2004": "Control char (three-per-em space)",
    "\u2005": "Control char (four-per-em space)",
    "\u2006": "Control char (six-per-em space)",
    "\u2007": "Control char (figure space)",
    "\u2008": "Control char (punctuation space)",
    "\u2009": "Control char (thin space)",
    "\u200a": "Control char (hair space)",
    "\u200b": "Control char (zero-width space)",
    "\u202f": "Control char (narrow no-break space)",
    "\u205f": "Control char (medium mathematical space)",
    "\u3000": "Control char (ideographic space)",
    "\ufeff": "Control char (byte order mark)",
    "\u2800": "Braille pattern blank",
    "\u061c": "Arabic letter mark",
    "\u1160": "Hangul Jungseong Filler",
    "\u115f": "Hangul Choseong Filler",
    "\u17b4": "Khmer Vowel Inherent Aq",
    "\u17b5": "Khmer Vowel Inherent Aa",
    "\U0001d173": "Musical symbol begin beam",
    "\U0001d174": "Musical symbol end beam",
    "\U0001d175": "Musical symbol begin tie",
    "\U0001d176": "Musical symbol end tie",
    "\U0001d177": "Musical symbol begin slur",
    "\U0001d178": "Musical symbol end slur",
    "\U0001d179": "Musical symbol begin phrase",
    "\U0001d17a": "Musical symbol end phrase",
    "\u3164": "Hangul filler",
}


def find_hidden_chars(lines: list[str], start_line: int = 1) -> list[Token]:
    hidden_char_indexes: list[tuple[tuple[int, int], str]] = [
        ((line_index + start_line, char_index), char)
        for line_index, line in enumerate(lines)
        for char_index, char in enumerate(line)
        if char in list(hidden_chars.keys())
    ]
    tok_list: list[Token] = [
        (char[0], len(char[1]), "Hidden_Char") for char in hidden_char_indexes
    ]
    return tok_list


def get_highlights(
    full_text: str,
    language: str = "text",
    text_range: tuple[int, int] = (1, -1),
) -> list[Token]:
    """Gets pygments tokens from text provided in language proved and converts them to Token's"""
    lexer: Lexer = get_lexer_by_name(language)
    split_text: list[str] = full_text.splitlines()
    new_tokens: list[Token] = []
    if text_range[1] == -1:
        text_range = (text_range[0], len(split_text))
    start_index: tuple[int, int] = (text_range[0], 0)
    split_text = split_text[text_range[0] - 1 : text_range[1]]

    for line in split_text:
        og_tokens: list[tuple[_TokenType, str]] = list(lex(line, lexer))
        for token in og_tokens:
            new_type: str = get_new_token_type(str(token[0]))
            token_str: str = token[1]
            token_len: int = len(token_str)

            if token_str == "\n":  # Lexer adds the newline back
                continue
            if not token_str.strip() and new_type == "Text":
                start_index = (start_index[0], start_index[1] + token_len)
                continue

            new_token = (start_index, token_len, new_type)
            new_tokens.append(new_token)

            start_index = (start_index[0], start_index[1] + token_len)
        start_index = (start_index[0] + 1, 0)

    # Add extra token types
    new_tokens += get_urls(split_text, text_range[0])
    if [char for char in hidden_chars if char in full_text]:
        new_tokens += find_hidden_chars(split_text, text_range[0])

    return new_tokens


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
