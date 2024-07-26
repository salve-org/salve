from functools import cache
from re import DOTALL, MULTILINE, Match, compile

from beartype.typing import Callable
from pygments.lexer import RegexLexer, default
from pygments.token import Comment as CommentToken
from pygments.token import String as StringToken  # noqa: F811
from token_tools import Token

from .misc import get_new_token_type

useful_tokens = {
    StringToken.Doc,
    StringToken.Heredoc,
    CommentToken,
    CommentToken.Multiline,
}

# Beartype speed optimizations
_TokenType = type(StringToken)  # Resolves to pygments.token._TokenType
_TokenTupleInternalType = tuple[_TokenType | Callable, ...]
_TokenTupleReturnType = list[tuple[str, _TokenType]]
_ListOfStrs = list[str]
_LexReturnTokens = list[tuple[_TokenType, str]]


@cache
def get_pygments_comment_regexes(lexer: RegexLexer) -> _TokenTupleReturnType:
    """
    Steals the regexes that pygments uses to give docstring, heredoc, comment, and multiline comment highlights
    (css comments, though multiline, aren't called multiline comments)
    """

    regexes: _TokenTupleReturnType = []

    for path in lexer.tokens:
        # This should have a better type definition, but I didn't have the mental capacity to
        # write each possibility, so I'm waiting for beartype to implement the functionality for me like the bum I am
        path_tokens: list = lexer.tokens[path]

        if isinstance(path_tokens[0], str):
            # This means that the path is redirecting to another path in its place,
            # but we check them all anyway so just exit this path
            continue

        for token_tuple in path_tokens:
            # Ensure that this is actually a tuple and not a random type
            if isinstance(token_tuple, default):
                continue

            if token_tuple[1] in useful_tokens:
                regexes.append((token_tuple[0], token_tuple[1]))
                continue

            # The Token tuple SHOULD be a callable at this point
            if not callable(token_tuple[1]):
                continue

            pygments_func: Callable = token_tuple[1]

            if pygments_func.__closure__ is None:
                # Will always evaluate to False, but it's for the static type checkers appeasement
                continue

            tokens: _TokenTupleInternalType = [
                cell.cell_contents for cell in token_tuple[1].__closure__
            ][
                0
            ]  # Sometimes pygments hides these types in functional programming

            for token in tokens:
                if token in useful_tokens:
                    # We know if it's in the useful tokens list that
                    # it's a token type but the static type checker doesn't
                    regexes.append((token_tuple[0], token))  # type: ignore
                    continue

    return list(set(regexes))  # type: ignore


def proper_docstring_tokens(lexer: RegexLexer, full_text: str) -> list[Token]:
    proper_highlight_regexes: _TokenTupleReturnType = (
        get_pygments_comment_regexes(lexer)
    )

    new_docstring_tokens: list[Token] = []
    split_text: _ListOfStrs = full_text.splitlines()

    for regex, token_type in proper_highlight_regexes:
        current_text = full_text
        match: Match[str] | None = compile(
            regex, flags=MULTILINE | DOTALL
        ).search(full_text)

        if match is None:
            # Onwards to the next regex!
            continue

        start_pos: tuple[int, int] = (1, 0)
        simple_token_type: str = get_new_token_type(str(token_type))

        while match:
            span: tuple[int, int] = match.span()
            matched_str: str = current_text[span[0] : span[1]]

            # Remove any whitespace previous to the match and update span accordingly
            matched_len_initial: int = len(matched_str)
            matched_str = matched_str.lstrip()
            matched_len_lstripped: int = len(matched_str)
            span = (
                (span[0] + matched_len_initial - matched_len_lstripped),
                span[1],
            )

            # Other useful variables without relation
            newline_count: int = matched_str.count("\n")
            previous_text: str = current_text[: span[0]]

            start_line: int = previous_text.count("\n") + start_pos[0]

            # Deal with the easy case first
            if not newline_count:
                # Prepare token variables
                start_col: int = split_text[start_line].find(matched_str)
                current_text: str = full_text[span[0] + span[1] - span[0] :]

                # Create and add token
                token: Token = (
                    (start_line, start_col),
                    matched_len_lstripped,
                    simple_token_type,
                )
                new_docstring_tokens.append(token)

                start_pos = (start_line, start_col + matched_len_lstripped)
                current_text = current_text[: span[1]]

                # Continue onward!
                match = compile(regex, flags=MULTILINE).search(current_text)
                continue

            # Now for multiple line matches
            split_match: list[str] = matched_str.splitlines()
            for i in range(newline_count + 1):
                match_str: str = split_match[i]
                initial_len: int = len(match_str)
                start_col: int = initial_len - len(match_str.lstrip())

                if i == 0:
                    line: str = split_text[start_line - 1]

                    true_len: int = len(line)
                    lstripped_len: int = len(line.lstrip())
                    initial_len = lstripped_len
                    if lstripped_len != true_len:
                        # In case the regex doesn't skip whitespace/junk
                        initial_len = true_len

                    start_col = line.find(match_str)

                # Create and add token
                token: Token = (
                    (start_line + i, start_col),
                    initial_len - start_col,
                    simple_token_type,
                )
                new_docstring_tokens.append(token)

                start_pos = (start_line + i, start_col + len(match_str))

            # Continue onward!
            current_text = current_text[span[1] :]
            match = compile(regex, flags=MULTILINE).search(current_text)

    return new_docstring_tokens
