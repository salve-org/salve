from functools import cache

from pygments import lex
from pygments.lexer import Lexer, RegexLexer
from pygments.lexers import get_lexer_by_name

from .docstring_highlight import _LexReturnTokens, proper_docstring_tokens
from .links_and_hidden_chars import find_hidden_chars, get_urls, hidden_chars
from .tokens import (
    Token,
    get_new_token_type,
    only_tokens_in_text_range,
    overwrite_and_merge_tokens,
)


@cache
def lexer_by_name_cached(language: str) -> Lexer:
    return get_lexer_by_name(language)


def get_highlights(
    full_text: str,
    language: str = "text",
    text_range: tuple[int, int] = (1, -1),
) -> list[Token]:
    """Gets pygments tokens from text provided in language proved and converts them to Token's"""

    # Create some variables used all throughout the function
    lexer: Lexer = lexer_by_name_cached(language)
    split_text: list[str] = full_text.splitlines()
    new_tokens: list[Token] = []

    if text_range[1] == -1:
        # This indicates that the text range should span the length of the entire code
        text_range = (text_range[0], len(split_text))

    start_index: tuple[int, int] = (text_range[0], 0)
    # We want only the lines in the text range because this list is iterated
    split_text: list[str] = split_text[text_range[0] - 1 : text_range[1]]

    for line in split_text:
        og_tokens: _LexReturnTokens = list(lex(line, lexer))
        for token in og_tokens:
            new_type: str = get_new_token_type(str(token[0]))
            token_str: str = token[1]
            token_len: int = len(token_str)

            if token_str == "\n":
                # Lexer adds the newline back as its own token
                continue

            if not token_str.strip() and new_type == "Text":
                # If the token is empty or is plain Text we simply skip it because thats ultimately useless info
                start_index = (start_index[0], start_index[1] + token_len)
                continue

            # Create and append the Token that will be returned
            new_token = (start_index, token_len, new_type)
            new_tokens.append(new_token)

            start_index = (start_index[0], start_index[1] + token_len)
        start_index = (start_index[0] + 1, 0)

    if isinstance(lexer, RegexLexer):
        new_tokens = overwrite_and_merge_tokens(
            new_tokens, proper_docstring_tokens(lexer, full_text)
        )

    new_tokens += get_urls(split_text, text_range[0])
    if [char for char in hidden_chars if char in full_text]:
        # if there are not hidden chars we don't want to needlessly compute this
        new_tokens += find_hidden_chars(split_text, text_range[0])

    new_tokens = only_tokens_in_text_range(new_tokens, text_range)
    return new_tokens
