<h1 align="center">Salve v0.6.0</h1>

# Installation

In the Command Line, paste the following: `pip install salve_ipc`

## Description

Salve is an IPC library that can be used by code editors to easily get autocompletions, replacements, editorconfig suggestions, definitions, and syntax highlighting.

> **Note**
> The first time that the system is loaded or a new server needs to be started it will take a fair bit longer

## Documentation

### `Token` type alias

The `Token` type alias helps your type checker when you work with `Token`'s from salve.

### `generic_tokens`

The `generic_tokens` list is a list of strings that define all of the generic token types returned by the server which can be mapped to colors for syntax highlighting.

### `hidden_chars`

The `hidden_chars` (`dict[str, str]`) dictionary holds a bunch of hidden (zero width) characters as keys and then names for them as values. `Token`'s of type "Hidden_Char" give the index to hidden characters and allow the user to display hidden characters to them that they may not see. These characters appear in code posted on forums or blogs by those hoping to prevent others from simply copy-pasting their code along with many other places.

### `Response` TypedDict class

The `Response` TypedDict classs allows for type checking when handling output from salve_ipc.

### `is_unicode_letter(char: str) -> bool`

The `is_unicode_letter()` function returns a boolean if a given word is a unicode letter (includes "\_" as special case) which can be useful when trying to find the current word being typed to hand to the IPC for autocompletion.

### `IPC` Class

| Method | Description | Arguments | Return type |
| - | - | - | - |
| `.request_autocomplete()` | Requests autocompletions from the server | `file`: str, `expected_keywords`: list[str], `current_word`: str | None |
| `.request_replacements()` | Requests replacement suggestions from the server | `file`: str, `expected_keywords`: list[str], `current_word`: str | None |
| `.request_highlight()` | Requests highlighting tokens from the server | `file`: str, `language`: str | None |
| `.request_editorconfig()` | Requests editorconfig details from the server | `file_path`: Path or str | None |
| `.request_definition()` | Requests definition locations from the server | `file`: str, `definition_starters`: list[tuple[str, str]], `current_word`: str | None |
| `.cancel_autocomplete_request()` | Cancels requests for autocompletions | None | None |
| `.cancel_replacements_request()` | Cancels requests for replacements| None | None |
| `.cancel_highlight_request()` | Cancels requests for highlighting| None | None |
| `.cancel_editorconfig_request()` | Cancels requests for editorconfig details | None | None |
| `.cancel_definition_request()` | Cancels requests for defnition | None | None |
| `.get_autocomplete_response()` | Gets newest autocomplete response from the server if any| None | Response \| None |
| `.get_replacements_response()` | Gets newest replacement response from the server if any | None | Response \| None |
| `.get_highlight_response()` | Gets newest highlight response from the server if any | None | Response \| None |
| `.get_editorconfig_response()` | Gets newest editorconfig response from the server if any| None | Response \| None |
| `.get_definition_response()` | Gets newest definition response from the server if any| None | Response \| None |
| `.update_file()` | Updates files stored on the server that are used to get responses| `file`: str, `current_state`: str (just the text of the file) | None |
| `.remove_file()` | Removes a file of the name given if any exists. Files should only be removed after all requests using the file are completed. | `file`: str | None |
| `.kill_IPC()` | This kills the IPC process and acts as a precaution against wasted CPU | None | None |

### Basic Usage:

```python
from time import sleep

from salve_ipc import IPC, Response


def main():
    context = IPC()

    context.update_file(
        "test",
        open(__file__, "r+").read() * 20,
    )

    context.request_highlight(file="test", language="python", text_range=(1, 30))

    sleep(1)
    output: Response | None = context.get_highlight_response()
    print(output)
    context.kill_IPC()


if __name__ == "__main__":
    main()
```

## How to run and contribute

### Running

To run the example, move `examples/example_usage.py` to the root directory and run with python.

To test newer features or test code in a Pull Review, do the same but move it back after if you plan to make a PR.

### Contributing

To contribute, fork the repository, make your changes, and then make a pull request. If you want to add a feature, please open an issue first so it can be discussed. Note that whenever and wherever possible you should try to use stdlib modules rather than external ones.

## License

This project is licensed under the MIT License - see the [LICENSE](./LISCENSE).
