from dataclasses import dataclass
from re import Match, Pattern, compile

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
    "Link",  # Website link (Not given by pygments)
]


@dataclass
class Token:
    """Generic Token class that makes highlighting files simple and easy"""

    start_index: tuple[int, int]  # line, column
    token_length: int
    highlight_type: str


def tokens_from_result(result: list[str]) -> list[Token]:
    """Returns a list of Token's given as a result (converted to str) that can be used for highlighting"""
    tokens: list[Token] = []
    for token in result:
        try:
            split_token = token.split("=")[1:4]

            start_index_parens = split_token[0].split(",")[0:2]
            line: int = int(start_index_parens[0].split("(")[1])
            column: int = int(start_index_parens[1].split(")")[0])
            start_index: tuple[int, int] = (line, column)

            token_length: int = int(split_token[1].split(",")[0])

            highlight_type: str = split_token[2].split("'")[1]

            real_token = Token(start_index, token_length, highlight_type)
            tokens.append(real_token)
        except IndexError:
            raise Exception("Could not parse results! Not highlight tokens!")
    return tokens


def get_new_token_type(old_token: str) -> str:
    """Turns pygments token types into a generic predefined Token"""
    new_type: str = generic_tokens[0]
    for index, token in enumerate(default_tokens):
        if token.startswith(old_token):
            new_type = generic_tokens[index]
            break
    return new_type


url_regex: Pattern = compile(r"(ftp|http|https):\/\/[a-zA-Z0-9_-]")


def get_urls(full_text: str) -> list[Token]:
    start_pos: tuple[int, int] = (1, 0)
    lines: list[str] = full_text.splitlines()
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


def get_highlights(full_text: str, language: str = "text") -> list[Token]:
    """Gets pygments tokens from text provided in language proved and converts them to Token's"""
    lexer: Lexer = get_lexer_by_name(language)
    new_tokens: list[Token] = []
    og_tokens: list[tuple[_TokenType, str]] = list(lex(full_text, lexer))
    start_index: tuple[int, int] = (1, 0)

    for token in og_tokens:
        new_type: str = get_new_token_type(str(token[0]))
        token_str: str = token[1]
        token_len: int = len(token_str)
        new_token = Token(start_index, token_len, new_type)
        new_tokens.append(new_token)

        if token_str == "\n":
            start_index = (start_index[0] + 1, 0)
            continue

        start_index = (start_index[0], start_index[1] + token_len)

    new_tokens += get_urls(
        full_text
    )  # Links can be useful for editors and they can always choose to discard them

    return new_tokens
