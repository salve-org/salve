from functools import cache

from token_tools import GENERIC_TOKENS

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


def normal_text_range(
    full_text: str, text_range: tuple[int, int] = (1, -1)
) -> tuple[list[str], tuple[int, int]]:
    split_text: list[str] = full_text.splitlines()

    if text_range[1] == -1:
        # This indicates that the text range should span the length of the entire code
        text_range = (text_range[0], len(split_text))

    # We want only the lines in the text range because this list is iterated
    split_text = split_text[text_range[0] - 1 : text_range[1]]

    return (split_text, text_range)


@cache
def get_new_token_type(old_token: str) -> str:
    """Turns pygments token types into a generic predefined Token"""
    new_type: str = GENERIC_TOKENS[0]
    for index, token in enumerate(default_tokens):
        if old_token.startswith(token):
            new_type = GENERIC_TOKENS[index]
            break
    return new_type
