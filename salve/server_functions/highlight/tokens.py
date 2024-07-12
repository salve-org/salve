from functools import cache

from pygments.token import String as StringToken

_TokenType = type(StringToken)  # Resolves to pygments.token._TokenType

Token = tuple[tuple[int, int], int, str]

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
    "Definition",  # Definitions
]

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


@cache
def get_new_token_type(old_token: str) -> str:
    """Turns pygments token types into a generic predefined Token"""
    new_type: str = generic_tokens[0]
    for index, token in enumerate(default_tokens):
        if old_token.startswith(token):
            new_type = generic_tokens[index]
            break
    return new_type


def only_tokens_in_text_range(
    tokens: list[Token], text_range: tuple[int, int]
) -> list[Token]:
    # We create a new list because lists are pass by reference
    output_tokens: list[Token] = []

    for token in tokens:
        token_lineno: int = token[0][0]
        minimum_line: int = text_range[0]
        maximum_line: int = text_range[1]

        if token_lineno < minimum_line or token_lineno > maximum_line:
            continue

        output_tokens.append(token)

    output_tokens = merge_tokens(output_tokens)
    return output_tokens


def merge_tokens(tokens: list[Token]) -> list[Token]:
    output_tokens: list[Token] = []
    depth: int = 0
    for token in tokens:
        # Deal with basic edge case
        if depth == 0:
            output_tokens.append(token)
            depth += 1
            continue

        previous_token = output_tokens[-1]

        # Get our boolean checks
        same_token_type: bool = previous_token[2] == token[2]
        same_line: bool = previous_token[0][0] == token[0][0]
        neighboring_tokens: bool = (
            previous_token[0][1] + previous_token[1] == token[0][1]
        )

        # Determine if tokens should be merged
        if not (same_token_type and same_line and neighboring_tokens):
            output_tokens.append(token)
            depth += 1
            continue

        # Replace previous token with new token (we don't increase depth because we are substituting, not adding)
        new_token: Token = (
            (token[0][0], previous_token[0][1]),
            previous_token[1] + token[1],
            token[2],
        )
        output_tokens[-1] = new_token
    return output_tokens


def overwrite_tokens(
    old_tokens: list[Token], new_tokens: list[Token]
) -> list[Token]:
    if not new_tokens:
        return old_tokens

    output_tokens: list[Token] = []
    dont_add_tokens: list[Token] = []
    for new_token in new_tokens:
        for old_token in old_tokens:
            same_token: bool = old_token == new_token
            if same_token:
                continue

            same_line: bool = old_token[0][0] == new_token[0][0]
            can_add_token: bool = old_token not in dont_add_tokens
            if not same_line:
                if can_add_token:
                    output_tokens.append(old_token)
                continue

            # Check if the ranges overlap and if so either (remove the old_token and add to don't add list) or,
            # if part of the token is out of the new_token_range, remove the part in the new tokens range

            old_token_end: int = old_token[0][1] + old_token[1]
            new_token_end: int = new_token[0][1] + new_token[1]

            partial_front_overlap: bool = (
                new_token[0][1] <= old_token_end
                and not old_token_end > new_token_end
            )
            partial_end_overlap: bool = new_token_end >= old_token[0][1]
            fully_contained: bool = (
                old_token_end <= new_token_end
                and old_token[0][1] >= new_token[0][1]
            )

            if not (
                partial_front_overlap or partial_end_overlap or fully_contained
            ):
                continue

            dont_add_tokens.append(old_token)

            while old_token in output_tokens:
                output_tokens.remove(old_token)

            if fully_contained:
                continue

            # If we are here if means it's a partial overlap
            if partial_front_overlap:
                created_token: Token = (
                    (new_token[0][0], old_token[0][1]),
                    new_token[0][1] - old_token[0][1],
                    old_token[2],
                )
                while created_token in output_tokens:
                    output_tokens.remove(created_token)
                output_tokens.append(created_token)
                dont_add_tokens.append(created_token)
                continue

            if old_token[0][1] < new_token[0][1]:
                created_token_1: Token = (
                    (new_token[0][0], old_token[0][1]),
                    new_token[0][1] - old_token[0][1],
                    old_token[2],
                )
                created_token_2: Token = (
                    (new_token[0][0], new_token_end),
                    old_token_end - new_token_end,
                    old_token[2],
                )
                while created_token_1 in output_tokens:
                    output_tokens.remove(created_token_1)
                output_tokens.append(created_token_1)
                while created_token_2 in output_tokens:
                    output_tokens.remove(created_token_2)
                output_tokens.append(created_token_2)
                dont_add_tokens.append(created_token_1)
                dont_add_tokens.append(created_token_2)

            created_token: Token = (
                (new_token[0][0], new_token_end),
                old_token_end - new_token_end,
                old_token[2],
            )
            while created_token in output_tokens:
                output_tokens.remove(created_token)
            output_tokens.append(created_token)
            dont_add_tokens.append(created_token)

        output_tokens.append(new_token)

    output_tokens = sorted(set(output_tokens))
    return output_tokens


def overwrite_and_merge_tokens(
    old_tokens: list[Token], new_tokens: list[Token]
) -> list[Token]:
    merged_old_tokens: list[Token] = merge_tokens(sorted(set(old_tokens)))
    merged_new_tokens: list[Token] = merge_tokens(sorted(set(new_tokens)))
    output_tokens: list[Token] = overwrite_tokens(
        merged_old_tokens, merged_new_tokens
    )

    output_tokens = sorted(set(merge_tokens(output_tokens)))
    return output_tokens
