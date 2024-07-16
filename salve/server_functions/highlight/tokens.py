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
    # If there are no new tokens, return the old tokens as they are
    if not new_tokens:
        return old_tokens

    # List to hold the final set of tokens
    output_tokens: list[Token] = []
    # List to track tokens that should not be added again
    dont_add_tokens: list[Token] = []

    # Iterate over each new token
    for new_token in new_tokens:
        # Extract the new token's properties
        new_start: tuple[int, int] = new_token[0]
        new_line: int = new_start[0]
        new_start_col: int = new_start[1]
        new_length: int = new_token[1]
        new_end_col: int = new_start_col + new_length

        # Iterate over each old token
        for old_token in old_tokens:
            # Extract the old token's properties
            old_start: tuple[int, int] = old_token[0]
            old_line: int = old_start[0]
            old_start_col: int = old_start[1]
            old_length: int = old_token[1]
            old_end_col: int = old_start_col + old_length
            old_type: str = old_token[2]

            # If the old and new tokens are the same, skip processing
            if old_token == new_token:
                continue

            # If tokens are on different lines, add the old token to output if it's not already added
            if old_line != new_line:
                if old_token not in dont_add_tokens:
                    output_tokens.append(old_token)
                continue

            # Check for no overlap (old token is entirely before or after the new token)
            if old_end_col <= new_start_col or old_start_col >= new_end_col:
                if old_token not in dont_add_tokens:
                    output_tokens.append(old_token)
                continue

            # Since there's overlap, mark the old token to avoid re-adding it
            dont_add_tokens.append(old_token)

            # Remove any instances of the old token
            while old_token in output_tokens:
                output_tokens.remove(old_token)

            # Handle partial overlap where the old token starts before the new token
            if old_start_col < new_start_col:
                left_token: Token = (
                    (old_line, old_start_col),
                    new_start_col - old_start_col,
                    old_type,
                )
                output_tokens.append(left_token)

            # Handle partial overlap where the old token ends after the new token
            if old_end_col > new_end_col:
                right_token: Token = (
                    (old_line, new_end_col),
                    old_end_col - new_end_col,
                    old_type,
                )
                output_tokens.append(right_token)

        # Add the new token to the output list
        output_tokens.append(new_token)

    # Sort the output tokens to ensure they are in the correct order
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
