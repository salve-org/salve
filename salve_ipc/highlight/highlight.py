from dataclasses import dataclass

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
    start_index: tuple[int, int]  # line, column
    token_length: int
    highlight_type: str


def tokens_from_result(result: list[str]) -> list[Token]:
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
