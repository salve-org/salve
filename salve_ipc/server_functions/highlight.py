from re import MULTILINE, Match, Pattern, compile

from beartype.typing import Callable
from pygments import lex
from pygments.lexer import Lexer, RegexLexer, default
from pygments.lexers import get_lexer_by_name
from pygments.token import Comment as CommentToken
from pygments.token import String as StringToken

from .misc import Token, generic_tokens

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


def get_new_token_type(old_token: str) -> str:
    """Turns pygments token types into a generic predefined Token"""
    new_type: str = generic_tokens[0]
    for index, token in enumerate(default_tokens):
        if old_token.startswith(token):
            new_type = generic_tokens[index]
            break
    return new_type


url_regex: Pattern = compile(r"(ftp|http|https):\/\/[a-zA-Z0-9_-]")


def get_urls(lines: list[str], start_line: int = 1) -> list[Token]:
    start_pos: tuple[int, int] = (start_line, 0)
    url_toks: list[Token] = []
    while True:
        if start_pos[0] >= len(lines) + start_line:
            break
        line: str = lines[start_pos[0] - start_line][start_pos[1] :]
        match_start: Match[str] | None = url_regex.search(line)
        if match_start is None:
            start_pos = (start_pos[0] + 1, 0)
            continue
        token_start_col = match_start.span()[0]  # type: ignore
        url: str = line[token_start_col:]

        # Narrow down the url
        url = url.strip()
        url = url.split()[0]
        url = url.split("'")[0]
        url = url.split("`")[0]
        url = url.split('"')[0]
        url = url.rstrip(".,?!")
        if "(" not in url:  # urls can contain spaces (e.g. wikipedia)
            url = url.rstrip(")")
        url = url.rstrip(".,?!")

        url_len: int = len(url)
        token: Token = ((start_pos[0], token_start_col), url_len, "Link")
        url_toks.append(token)
        start_pos = (start_pos[0], start_pos[1] + url_len + token_start_col)

    return url_toks


hidden_chars: dict[str, str] = {
    "\u0009": "CHARACTER TABULATION",
    "\u00a0": "NO-BREAK SPACE",
    "\u00ad": "SOFT HYPHEN",
    "\u034f": "COMBINING GRAPHEME JOINER",
    "\u061c": "ARABIC LETTER MARK",
    "\u115f": "HANGUL CHOSEONG FILLER",
    "\u1160": "HANGUL JUNGSEONG FILLER",
    "\u17b4": "KHMER VOWEL INHERENT AQ",
    "\u17b5": "KHMER VOWEL INHERENT AA",
    "\u180e": "MONGOLIAN VOWEL SEPARATOR",
    "\u2000": "EN QUAD",
    "\u2001": "EM QUAD",
    "\u2002": "EN SPACE",
    "\u2003": "EM SPACE",
    "\u2004": "THREE-PER-EM SPACE",
    "\u2005": "FOUR-PER-EM SPACE",
    "\u2006": "SIX-PER-EM SPACE",
    "\u2007": "FIGURE SPACE",
    "\u2008": "PUNCTUATION SPACE",
    "\u2009": "THIN SPACE",
    "\u200a": "HAIR SPACE",
    "\u200b": "ZERO WIDTH SPACE",
    "\u200c": "ZERO WIDTH NON-JOINER",
    "\u200d": "ZERO WIDTH JOINER",
    "\u200e": "LEFT-TO-RIGHT MARK",
    "\u200f": "RIGHT-TO-LEFT MARK",
    "\u202f": "NARROW NO-BREAK SPACE",
    "\u205f": "MEDIUM MATHEMATICAL SPACE",
    "\u2060": "WORD JOINER",
    "\u2061": "FUNCTION APPLICATION",
    "\u2062": "INVISIBLE TIMES",
    "\u2063": "INVISIBLE SEPARATOR",
    "\u2064": "INVISIBLE PLUS",
    "\u206a": "INHIBIT SYMMETRIC SWAPPING",
    "\u206b": "ACTIVATE SYMMETRIC SWAPPING",
    "\u206c": "INHIBIT ARABIC FORM SHAPING",
    "\u206d": "ACTIVATE ARABIC FORM SHAPING",
    "\u206e": "NATIONAL DIGIT SHAPES",
    "\u206f": "NOMINAL DIGIT SHAPES",
    "\u3000": "IDEOGRAPHIC SPACE",
    "\u2800": "BRAILLE PATTERN BLANK",
    "\u3164": "HANGUL FILLER",
    "\ufeff": "ZERO WIDTH NO-BREAK SPACE",
    "\uffa0": "HALFWIDTH HANGUL FILLER",
    "\u1d159": "MUSICAL SYMBOL NULL NOTEHEAD",
    "\u1d173": "MUSICAL SYMBOL BEGIN BEAM",
    "\u1d174": "MUSICAL SYMBOL END BEAM",
    "\u1d175": "MUSICAL SYMBOL BEGIN TIE",
    "\u1d176": "MUSICAL SYMBOL END TIE",
    "\u1d177": "MUSICAL SYMBOL BEGIN SLUR",
    "\u1d178": "MUSICAL SYMBOL END SLUR",
    "\u1d179": "MUSICAL SYMBOL BEGIN PHRASE",
    "\u1d17A": "MUSICAL SYMBOL END PHRASE",
    "\ue0020": "TAG SPACE",
}


def find_hidden_chars(lines: list[str], start_line: int = 1) -> list[Token]:
    hidden_char_indexes: list[tuple[tuple[int, int], str]] = [
        ((line_index + start_line, char_index), char)
        for line_index, line in enumerate(lines)
        for char_index, char in enumerate(line)
        if char in list(hidden_chars.keys())
    ]
    tok_list: list[Token] = [
        (char[0], len(char[1]), "Hidden_Char") for char in hidden_char_indexes
    ]
    return tok_list


# Instantiate some useful variables/types for the following functions
useful_toks = {
    StringToken.Doc,
    StringToken.Heredoc,
    CommentToken,
    CommentToken.Multiline,
}

# Beartype speed optimizations
_TokenType = type(StringToken) # Resolves to pygments.token._TokenType
_TokenTupleInternalType = tuple[_TokenType | Callable, ...]
_TokenTupleReturnType = list[tuple[str, _TokenType]]
_ListOfStrs = list[str]
_LexReturnTokens = list[tuple[_TokenType, str]]


def get_pygments_comment_regexes(lexer: RegexLexer) -> _TokenTupleReturnType:
    """
    Steals the regexes that pgments uses to give docstring, heredoc, comment, and multiline comment highlights
    (css comments, though multine, aren't called multiline comments)
    """

    regexes: _TokenTupleReturnType = []

    for path in lexer.tokens:
        # This should have a better type definition but I didn't have the mental capacity to
        # write each possibility so I'm waiting for beartype to implement the functionality for me like the bum I am
        path_tokens: list = lexer.tokens[path]

        if isinstance(path_tokens[0], str):
            # This means that the path is redirecting to another path in its place but we check them all anyway so just exit this path
            continue

        for token_tuple in path_tokens:
            # Ensure that this is actually a tuple and not a random type
            if isinstance(token_tuple, default):
                continue

            if token_tuple[1] in useful_toks:
                regexes.append((token_tuple[0], token_tuple[1]))
                continue

            # The Token tuple SHOULD be a callable at this point
            if not callable(token_tuple[1]):
                continue

            pygments_func: Callable = token_tuple[1]

            if pygments_func.__closure__ is None:
                # Will always evaluate to False but its for the static type checkers appeasement
                continue

            tokens: _TokenTupleInternalType = [
                cell.cell_contents for cell in token_tuple[1].__closure__
            ][
                0
            ]  # Sometimes pygments hides these types in functional programming

            for token in tokens:
                if token in useful_toks:
                    # We know if its in the useful tokens list that its a token type but the static type checker doesn't
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
        match: Match[str] | None = compile(regex, flags=MULTILINE).search(
            full_text
        )

        if match is None:
            # Onwards to the next regex!
            continue

        start_pos: tuple[int, int] = (0, 0)
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
                    line: str = split_text[start_line + i]

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


def get_highlights(
    full_text: str,
    language: str = "text",
    text_range: tuple[int, int] = (1, -1),
) -> list[Token]:
    """Gets pygments tokens from text provided in language proved and converts them to Token's"""

    # Create some variables used all throughout the function
    lexer: Lexer = get_lexer_by_name(language)
    split_text: _ListOfStrs = full_text.splitlines()
    new_tokens: list[Token] = []

    if text_range[1] == -1:
        # This indicates that the text range should span the length of the entire code
        text_range = (text_range[0], len(split_text))

    start_index: tuple[int, int] = (text_range[0], 0)
    # We want only the lines in the text range because this list is iterated
    split_text: _ListOfStrs = split_text[text_range[0] - 1 : text_range[1]]

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

    # Add extra token types
    # NOTE: we add these at the end so that when they are applied one by one by the editor these
    # override older tokens that may not be as accurate
    new_tokens += get_urls(split_text, text_range[0])
    if [char for char in hidden_chars if char in full_text]:
        # if there are not hidden chars we don't want to needlessly compute this
        new_tokens += find_hidden_chars(split_text, text_range[0])

    if isinstance(lexer, RegexLexer):
        new_tokens += proper_docstring_tokens(lexer, full_text)

    return new_tokens
