COMMANDS: list[str] = [
    "autocomplete",
    "replacements",
    "highlight",
    "editorconfig",
    "definition",
    "links_and_chars",
]

COMMAND = str
AUTOCOMPLETE: COMMAND = COMMANDS[0]
REPLACEMENTS: COMMAND = COMMANDS[1]
HIGHLIGHT: COMMAND = COMMANDS[2]
EDITORCONFIG: COMMAND = COMMANDS[3]
DEFINITION: COMMAND = COMMANDS[4]
LINKS_AND_CHARS: COMMAND = COMMANDS[5]
