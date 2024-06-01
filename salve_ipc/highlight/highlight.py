from dataclasses import dataclass
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


@dataclass
class Token:
    """Generic Token class that makes highlighting files simple and easy"""

    start_index: tuple[int, int]  # line, column
    token_length: int
    highlight_type: str

    def to_tuple(self) -> tuple[tuple[int, int], int, str]:
        return (self.start_index, self.token_length, self.highlight_type)


def tokens_from_result(
    result: list[tuple[tuple[int, int], int, str]]
) -> list[Token]:
    """Returns a list of Token's given as a result (converted to tuples) that can be used for highlighting"""
    tokens: list[Token] = []
    for token in result:
        try:
            real_token = Token(token[0], token[1], token[2])
            tokens.append(real_token)
        except IndexError:
            raise Exception("Could not parse results! Not highlight tokens!")
    return tokens


def get_new_token_type(old_token: str) -> str:
    """Turns pygments token types into a generic predefined Token"""
    new_type: str = generic_tokens[0]
    for index, token in enumerate(default_tokens):
        if old_token.startswith(token):
            new_type = generic_tokens[index]
            break
    return new_type


url_regex: Pattern = compile(r"(ftp|http|https):\/\/[a-zA-Z0-9_-]")


def get_urls(lines: list[str]) -> list[Token]:
    start_pos: tuple[int, int] = (1, 0)
    url_toks: list[Token] = []
    while True:
        line: str = lines[start_pos[0] - 1][start_pos[1] :]
        match_start: Match[str] | None = url_regex.match(line)
        if not match_start:
            if len(lines) >= start_pos[0]:
                break
            start_pos = (start_pos[0] + 1, 0)
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
        token: Token = Token((start_pos[0], token_start_col), url_len, "Link")
        url_toks.append(token)
        start_pos = (start_pos[0], start_pos[1] + url_len)
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
    # "\u000a": "Line feed", # "\n" char
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


def find_hidden_chars(lines: list[str]) -> list[Token]:
    hidden_char_indexes: list[tuple[tuple[int, int], str]] = [
        ((line_index + 1, char_index), char)
        for line_index, line in enumerate(lines)
        for char_index, char in enumerate(line)
        if char in list(hidden_chars.keys())
    ]
    tok_list: list[Token] = [
        Token(char[0], len(char[1]), "Hidden_Char")
        for char in hidden_char_indexes
    ]
    return tok_list


def get_highlights(full_text: str, language: str = "text") -> list[Token]:
    """Gets pygments tokens from text provided in language proved and converts them to Token's"""
    lexer: Lexer = get_lexer_by_name(language)
    split_text: list[str] = full_text.splitlines()
    new_tokens: list[Token] = []
    start_index: tuple[int, int] = (1, 0)

    for line in split_text:
        og_tokens: list[tuple[_TokenType, str]] = list(lex(line, lexer))
        for token in og_tokens:
            new_type: str = get_new_token_type(str(token[0]))
            token_str: str = token[1]
            if token_str == "\n":  # Lexer adds the newline back
                continue

            token_len: int = len(token_str)
            new_token = Token(start_index, token_len, new_type)
            new_tokens.append(new_token)

            start_index = (start_index[0], start_index[1] + token_len)
        start_index = (start_index[0] + 1, 0)

    # Add extra token types
    new_tokens += get_urls(split_text)
    new_tokens += find_hidden_chars(split_text)

    return new_tokens
