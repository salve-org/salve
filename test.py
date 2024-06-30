from typing import Callable

from pygments.lexer import RegexLexer
from pygments.token import Comment as CommentToken
from pygments.token import String as StringToken
from pygments.token import _TokenType


def get_pygments_comment_regexes(lexer: RegexLexer) -> list[str]:
    root_tokens: list[str] | list[tuple[str, _TokenType]] = lexer.tokens[
        "root"
    ]

    if isinstance(root_tokens[0], str):
        root_tokens = lexer.tokens[root_tokens[0]]

    useful_toks = {
        StringToken.Doc,
        StringToken.Heredoc,
        CommentToken,
        CommentToken.Multiline,
    }
    regexes: list[str] = []

    for token_tuple in root_tokens:
        if token_tuple[1] in useful_toks:
            regexes.append(token_tuple[0])
            continue

        if not isinstance(token_tuple[1], Callable):
            continue

        pygments_func: Callable = token_tuple[1]

        if pygments_func.__closure__ is None:
            # No idea whats going on here
            print(token_tuple[1])
            continue

        tokens: tuple[_TokenType] = [
            cell.cell_contents for cell in token_tuple[1].__closure__
        ][0]

        if not tokens:
            continue

        for token in tokens:
            if token in useful_toks:
                regexes.append(token_tuple[0])
                continue

    return list(set(regexes))


if __name__ == "__main__":
    from pygments.lexers import CssLexer, PythonLexer

    assert get_pygments_comment_regexes(CssLexer()) == ["/\\*(?:.|\\n)*?\\*/"]
    assert get_pygments_comment_regexes(PythonLexer()) == [
        "^(\\s*)([rRuUbB]{,2})('''(?:.|\\n)*?''')",
        '^(\\s*)([rRuUbB]{,2})("""(?:.|\\n)*?""")',
    ]
