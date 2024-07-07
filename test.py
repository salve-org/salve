Token = tuple[tuple[int, int], int, str]

_RangeTokenDict = dict[int, list[tuple[range, str]]]


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

def overwrite_tokens(old_tokens: list[Token], new_tokens: list[Token]):
    output_tokens: list[Token] = []
    dont_add_tokens: list[Token] = []
    for new_token in new_tokens:
        for old_token in old_tokens:
            same_token: bool = old_token == new_token
            if same_token:
                continue

            same_line: bool = old_token[0][0] == new_token[0][0]
            can_add_token: bool = not old_token in dont_add_tokens
            if not same_line:
                if can_add_token:
                    output_tokens.append(old_token)
                continue

            # Check if the ranges overlap and if so either (remove the old_token and add to don't add list) or,
            # if part of the token is out of the new_token_range, remove the part in the new tokens range

            old_token_end: int = old_token[0][1] + old_token[1]
            new_token_end: int = new_token[0][1] + new_token[1]

            partial_front_overlap: bool = new_token[0][1] <= old_token_end and not old_token_end > new_token_end
            partial_end_overlap: bool = new_token_end >= old_token[0][1]
            fully_contained: bool = old_token_end <= new_token_end and old_token[0][1] >= new_token[0][1]

            if not (partial_front_overlap or partial_end_overlap or fully_contained):
                continue

            dont_add_tokens.append(old_token)

            while old_token in output_tokens:
                output_tokens.remove(old_token)

            if fully_contained:
                continue

            # If we are here if means its a partial overlap
            if partial_front_overlap:
                created_token: Token = (
                    (new_token[0][0], old_token[0][1]), new_token[0][1] - old_token[0][1], old_token[2]
                )
                output_tokens.append(created_token)
                dont_add_tokens.append(created_token)
                continue

            created_token: Token = (
                (new_token[0][0], new_token_end), old_token_end - new_token_end, old_token[2]
            )
            output_tokens.append(created_token)
            dont_add_tokens.append(created_token)

        output_tokens.append(new_token)

    output_tokens = sorted(set(output_tokens))
    return output_tokens


def overwrite_and_merge_tokens(
    old_tokens: list[Token], new_tokens: list[Token]
) -> list[Token]:
    merged_old_tokens: list[Token] = merge_tokens(old_tokens)
    merged_new_tokens: list[Token] = merge_tokens(new_tokens)
    output_tokens: list[Token] = overwrite_tokens(
        merged_old_tokens, merged_new_tokens
    )

    output_tokens = merge_tokens(output_tokens)
    return output_tokens



existing_tokens: list[Token] = [
    ((2, 0), 5, "Name"),
    ((2, 5), 1, "Punctuation"),
    ((2, 6), 1, "String"),
    ((2, 7), 3, "String"),
    ((2, 10), 1, "String"),
    ((2, 11), 1, "Punctuation"),
    ((3, 0), 3, "String"),
    ((4, -1), 2, "Test"),
    ((4, 0), 4, "Name"),
    ((4, 4), 1, "Punctuation"),
    ((4, 5), 4, "Name"),
    ((4, 9), 1, "Punctuation"),
    ((4, 9), 5, "Test"),
    ((4, 11), 5, "Test"),
    ((5, 0), 3, "String"),
    ((6, 0), 3, "Keyword"),
    ((6, 4), 1, "Name"),
    ((6, 5), 1, "Punctuation"),
    ((6, 6), 1, "Punctuation"),
    ((6, 7), 1, "Punctuation"),
    ((6, 9), 4, "Keyword"),
]

new_tokens: list[Token] = [
    ((3, 0), 3, "String"),
    ((4, 0), 10, "String"),
    ((5, 0), 3, "String"),
]

output: list[Token] = overwrite_and_merge_tokens(existing_tokens, new_tokens)

assert output == [
    ((2, 0), 5, "Name"),
    ((2, 5), 1, "Punctuation"),
    ((2, 6), 5, "String"),
    ((2, 11), 1, "Punctuation"),
    ((3, 0), 3, "String"),
    ((4, -1), 1, "Test"),  # Super important
    ((4, 0), 10, "String"),
    ((4, 10), 4, "Test"),  # Super important
    ((4, 11), 5, "Test"),  # Super important
    ((5, 0), 3, "String"),
    ((6, 0), 3, "Keyword"),
    ((6, 4), 1, "Name"),
    ((6, 5), 3, "Punctuation"),
    ((6, 9), 4, "Keyword"),
]
