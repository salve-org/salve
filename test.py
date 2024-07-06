from salve_ipc import Token


def overwrite_and_merge_tokens(
    old_tokens: list[Token], new_tokens: list[Token]
) -> list[Token]:
    final_tokens: list[Token] = []
    # Insert voodoo magic here
    return final_tokens


existing_tokens: list[Token] = [
    ((2, 0), 5, "Name"),
    ((2, 5), 1, "Punctuation"),
    ((2, 6), 1, "String"),
    ((2, 7), 3, "String"),
    ((2, 10), 1, "String"),
    ((2, 11), 1, "Punctuation"),
    ((3, 0), 3, "String"),
    ((4, 0), 4, "Name"),
    ((4, 4), 1, "Punctuation"),
    ((4, 5), 4, "Name"),
    ((4, 9), 1, "Punctuation"),
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
    ((2, 6), 6, "String"),
    ((3, 0), 3, "String"),
    ((4, 0), 10, "String"),
    ((5, 0), 3, "String"),
    ((6, 0), 3, "Keyword"),
    ((6, 4), 1, "Name"),
    ((6, 5), 3, "Punctuation"),
    ((6, 9), 4, "Keyword"),
]
