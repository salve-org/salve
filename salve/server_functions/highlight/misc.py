from functools import cache

from token_tools import GENERIC_TOKENS

default_tokens: dict[str, str | None] = {
    "Token.Text.Whitespace": None,
    "Token.Text": None,
    "Token.Error": GENERIC_TOKENS[1],
    "Token.Keyword": GENERIC_TOKENS[2],
    "Token.Name": GENERIC_TOKENS[0],
    "Token.Literal.String": GENERIC_TOKENS[4],
    "Token.Literal.Number": GENERIC_TOKENS[5],
    "Token.Literal": GENERIC_TOKENS[6],
    "Token.Operator": GENERIC_TOKENS[7],
    "Token.Punctuation": GENERIC_TOKENS[8],
    "Token.Comment": GENERIC_TOKENS[9],
    "Token.Generic": None,
}


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
def get_new_token_type(token: str) -> str | None:
    """Turns pygments token types into a generic predefined Token"""
    for old_token, new_token in default_tokens.items():
        if token.startswith(old_token):
            return new_token

    return None
