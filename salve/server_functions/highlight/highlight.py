from functools import cache

from pygments import lex
from pygments.lexer import Lexer, RegexLexer
from pygments.lexers import get_lexer_by_name
from token_tools import (
    Token,
    normal_text_range,
    only_tokens_in_text_range,
    overwrite_and_merge_tokens,
)

from .docstring_highlight import _LexReturnTokens, proper_docstring_tokens
from .misc import get_new_token_type


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
    new_tokens: list[Token] = []

    split_text, text_range = normal_text_range(full_text, text_range)

    start_index: tuple[int, int] = (text_range[0], 0)

    for line in split_text:
        og_tokens: _LexReturnTokens = list(lex(line, lexer))
        for token in og_tokens:
            new_type: str = get_new_token_type(str(token[0]))
            token_str: str = token[1]
            token_len: int = len(token_str)

            if token_str == "\n":
                # Lexer adds the newline back as its own token
                continue

            if not token_str.strip() or new_type == "Text":
                # If the token is empty or is plain Text we simply skip it because that's ultimately useless info
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

    new_tokens = only_tokens_in_text_range(new_tokens, text_range)
    return new_tokens
