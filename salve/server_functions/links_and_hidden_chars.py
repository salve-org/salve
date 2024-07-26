from re import Match, Pattern, compile

from token_tools import Token

url_regex: Pattern = compile(r"(ftp|http|https)://[a-zA-Z0-9_-]")


def get_urls(whole_text: str, text_range: tuple[int, int]) -> list[Token]:
    lines: list[str] = whole_text.splitlines()
    start_pos: tuple[int, int] = (text_range[0], 0)
    url_toks: list[Token] = []
    while True:
        if start_pos[0] > text_range[1]:
            break
        line: str = lines[start_pos[0] - text_range[0]][start_pos[1] :]
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


def find_hidden_chars(
    whole_text: str, text_range: tuple[int, int]
) -> list[Token]:
    lines: list[str] = whole_text.splitlines()
    hidden_char_indexes: list[tuple[tuple[int, int], str]] = [
        ((line_index + text_range[0], char_index), char)
        for line_index, line in enumerate(lines)
        for char_index, char in enumerate(line)
        if char in list(hidden_chars.keys())
    ]
    tok_list: list[Token] = [
        (char[0], len(char[1]), "Hidden_Char") for char in hidden_char_indexes
    ]
    return tok_list


def get_special_tokens(
    whole_text: str, text_range: tuple[int, int]
) -> list[Token]:
    return_tokens: list[Token] = []
    return_tokens.extend(get_urls(whole_text, text_range))
    if [char for char in hidden_chars if char in whole_text]:
        # If there are no hidden chars we don't want to needlessly compute this
        return_tokens.extend(find_hidden_chars(whole_text, text_range))
    return return_tokens
