from re import MULTILINE, Match, Pattern, compile

from beartype.typing import Callable
from pygments import lex
from pygments.lexer import Lexer, RegexLexer, default
from pygments.lexers import get_lexer_by_name
from pygments.token import Comment as CommentToken
from pygments.token import String as StringToken
from pygments.token import _TokenType

from .misc import Token, generic_tokens

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
    "\u0009": "CHARACTER TABULATION",
    "\u00a0": "NO-BREAK SPACE",
    "\u00ad": "SOFT HYPHEN",
    "\u034f": "COMBINING GRAPHEME JOINER",
    "\u061c": "ARABIC LETTER MARK",
    "\u115f": "HANGUL CHOSEONG FILLER",
    "\u1160": "HANGUL JUNGSEONG FILLER",
    "\u17b4": "KHMER VOWEL INHERENT AQ",
    "\u17b5": "KHMER VOWEL INHERENT AA",
    "\u180e": "MONGOLIAN VOWEL SEPARATOR",
    "\u2000": "EN QUAD",
    "\u2001": "EM QUAD",
    "\u2002": "EN SPACE",
    "\u2003": "EM SPACE",
    "\u2004": "THREE-PER-EM SPACE",
    "\u2005": "FOUR-PER-EM SPACE",
    "\u2006": "SIX-PER-EM SPACE",
    "\u2007": "FIGURE SPACE",
    "\u2008": "PUNCTUATION SPACE",
    "\u2009": "THIN SPACE",
    "\u200a": "HAIR SPACE",
    "\u200b": "ZERO WIDTH SPACE",
    "\u200c": "ZERO WIDTH NON-JOINER",
    "\u200d": "ZERO WIDTH JOINER",
    "\u200e": "LEFT-TO-RIGHT MARK",
    "\u200f": "RIGHT-TO-LEFT MARK",
    "\u202f": "NARROW NO-BREAK SPACE",
    "\u205f": "MEDIUM MATHEMATICAL SPACE",
    "\u2060": "WORD JOINER",
    "\u2061": "FUNCTION APPLICATION",
    "\u2062": "INVISIBLE TIMES",
    "\u2063": "INVISIBLE SEPARATOR",
    "\u2064": "INVISIBLE PLUS",
    "\u206a": "INHIBIT SYMMETRIC SWAPPING",
    "\u206b": "ACTIVATE SYMMETRIC SWAPPING",
    "\u206c": "INHIBIT ARABIC FORM SHAPING",
    "\u206d": "ACTIVATE ARABIC FORM SHAPING",
    "\u206e": "NATIONAL DIGIT SHAPES",
    "\u206f": "NOMINAL DIGIT SHAPES",
    "\u3000": "IDEOGRAPHIC SPACE",
    "\u2800": "BRAILLE PATTERN BLANK",
    "\u3164": "HANGUL FILLER",
    "\ufeff": "ZERO WIDTH NO-BREAK SPACE",
    "\uffa0": "HALFWIDTH HANGUL FILLER",
    "\u1d159": "MUSICAL SYMBOL NULL NOTEHEAD",
    "\u1d173": "MUSICAL SYMBOL BEGIN BEAM",
    "\u1d174": "MUSICAL SYMBOL END BEAM",
    "\u1d175": "MUSICAL SYMBOL BEGIN TIE",
    "\u1d176": "MUSICAL SYMBOL END TIE",
    "\u1d177": "MUSICAL SYMBOL BEGIN SLUR",
    "\u1d178": "MUSICAL SYMBOL END SLUR",
    "\u1d179": "MUSICAL SYMBOL BEGIN PHRASE",
    "\u1d17A": "MUSICAL SYMBOL END PHRASE",
    "\ue0020": "TAG SPACE",
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


def get_pygments_comment_regexes(
    lexer: RegexLexer,
) -> list[tuple[str, _TokenType]]:
    useful_toks = {
        StringToken.Doc,
        StringToken.Heredoc,
        # StringToken.Double,
        CommentToken,
        CommentToken.Multiline,
    }
    regexes: list[str] = []

    all_tokens = lexer.tokens
    for path in all_tokens:
        path_tokens: list = lexer.tokens[path]

        if isinstance(path_tokens[0], str):
            continue

        for token_tuple in path_tokens:
            if isinstance(token_tuple, default):
                continue

            if token_tuple[1] in useful_toks:
                regexes.append((token_tuple[0], token_tuple[1]))  # type: ignore
                continue

            if not isinstance(token_tuple[1], Callable):
                continue

            pygments_func: Callable = token_tuple[1]

            if pygments_func.__closure__ is None:
                # No idea whats going on here
                continue

            tokens: tuple[_TokenType | Callable, ...] = [
                cell.cell_contents
                for cell in token_tuple[1].__closure__  # type: ignore
            ][0]
            if not tokens:
                continue

            for token in tokens:
                if token in useful_toks:
                    regexes.append((token_tuple[0], token))  # type: ignore
                    continue

    return list(set(regexes))  # type: ignore


def proper_docstring_tokens(lexer: RegexLexer, full_text: str) -> list[Token]:
    proper_highlight_regexes: list[tuple[str, _TokenType]] = (
        get_pygments_comment_regexes(lexer)
    )
    new_docstring_tokens: list[Token] = []
    for regex, token_type in proper_highlight_regexes:
        match_strings = compile(regex, flags=MULTILINE).findall(full_text)
        for match in match_strings:
            while match[2] in full_text:
                if "\n" not in match[2]:
                    current_location = full_text.find(match[2])
                    line_location: int = full_text[:current_location].count(
                        "\n"
                    )
                    new_docstring_tokens.append(
                        (
                            (
                                line_location + 1,
                                full_text.splitlines()[line_location].find(
                                    match[2]
                                ),
                            ),
                            len(match[2]),
                            get_new_token_type(str(token_type)),
                        )
                    )
                    full_text = (
                        full_text[:current_location]
                        + "\n" * match[2].count("\n")
                        + full_text[current_location + len(match[2]) :]
                    )
                    continue

                current_location = full_text.find(match[2])
                start_line_location: int = full_text[:current_location].count(
                    "\n"
                )
                split_match: list[str] = match[2].splitlines()
                for i in range(len(split_match)):
                    new_docstring_tokens.append(
                        (
                            (
                                start_line_location + i + 1,
                                full_text.splitlines()[
                                    start_line_location + i
                                ].find(split_match[i]),
                            ),
                            len(split_match[i]),
                            get_new_token_type(str(token_type)),
                        )
                    )

                full_text = (
                    full_text[:current_location]
                    + "\n" * match[2].count("\n")
                    + full_text[current_location + len(match[2]) :]
                )

    return new_docstring_tokens


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

    # Override with new docstring/multiline comment highlights
    if not isinstance(lexer, RegexLexer):
        return new_tokens

    new_tokens += proper_docstring_tokens(lexer, full_text)

    return new_tokens
