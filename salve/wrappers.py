from pyeditorconfig import get_config
from token_tools import Token, normal_text_range

from .misc import Request
from .server_functions import (
    find_autocompletions,
    get_definition,
    get_highlights,
    get_replacements,
    get_special_tokens,
)


def get_replacements_request_wrapper(request: Request) -> list[str]:
    return get_replacements(
        full_text=request["file"],
        expected_keywords=request["expected_keywords"],  # type: ignore
        replaceable_word=request["current_word"],  # type: ignore
    )


def find_autocompletions_request_wrapper(request: Request) -> list[str]:
    return find_autocompletions(
        full_text=request["file"],
        expected_keywords=request["expected_keywords"],  # type: ignore
        replaceable_word=request["current_word"],  # type: ignore
    )


def get_highlights_request_wrapper(request: Request) -> list[Token]:
    return get_highlights(
        full_text=request["file"],
        language=request["language"],  # type: ignore
        text_range=request["text_range"],  # type: ignore
    )


def editorconfig_request_wrapper(request: Request) -> dict:
    return get_config(request["file_path"])  # type: ignore


def get_definition_request_wrapper(request: Request) -> Token:
    return get_definition(
        request["file"],
        request["definition_starters"],  # type: ignore
        request["current_word"],  # type: ignore
    )


def get_special_tokens_request_wrapper(request: Request) -> list[Token]:
    return get_special_tokens(
        request["file"],
        normal_text_range(request["file"], request["text_range"])[  # type: ignore
            1
        ],
    )
