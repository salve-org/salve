from pygments.lexers import CssLexer, PythonLexer

from salve_ipc import get_pygments_comment_regexes


def test_regex_stealing() -> None:
    assert get_pygments_comment_regexes(CssLexer()) == ["/\\*(?:.|\\n)*?\\*/"]
    assert get_pygments_comment_regexes(PythonLexer()) == [
        "^(\\s*)([rRuUbB]{,2})('''(?:.|\\n)*?''')",
        '^(\\s*)([rRuUbB]{,2})("""(?:.|\\n)*?""")',
    ]
