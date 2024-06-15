<h1 align="center">Salve v0.5.0</h1>

# Installation

In the Command Line, paste the following: `pip install salve_ipc`

## Description

Salve is an IPC library that can be used by code editors to easily get autocompletions, replacements, editorconfig suggestions, definitions, and syntax highlighting.

> **Note**
> The first time that the system is loaded or a new server needs to be started it will take a fair bit longer

## Documentation

### `COMMANDS`

The `COMMANDS` list contains all valid commands to request server output from. If multiple requests of different commands are made they will be kept and held seperately and can be retrieved seperately. Current commands are as follows:

- "autocomplete"
- "replacements"
- "highlight"
- "editorconfig"
- "definition"

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

| Method              | Description                                                                                                                                                                                                                                                                                                                                               | Arguments                                                                                                                                                                                                                                                                                                                  |
| ------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `.get_response()`   | Gets a response of the requested command                                                                                                                                                                                                                                                                                                                  | `command`: str                                                                                                                                                                                                                                                                                                             |
| `.request()`        | Makes a request to the server                                                                                                                                                                                                                                                                                                                             | `command`: str, `file`: str, `expected_keywords`: list[str] ("autocomple" or "replacements"), `current_word`: str ("autocomple" or "replacements", "definition"), `language`: str ("highlight"), `text_range`: tuple[int, int] ("highlight"), `file_path`: pathlib.Path, str, `definition_starters`: list[tuple[str, str]] |
| `.cancel_request()` | Cancels request of command type and removes reponse if it was recieved. Must be called before `.get_response()` to work                                                                                                                                                                                                                                   | `command`: str                                                                                                                                                                                                                                                                                                             |
| `.update_file()`    | Updates files stored on the server that are used to get responses                                                                                                                                                                                                                                                                                         | `filename`: str, `current_state`: str (just the text of the file)                                                                                                                                                                                                                                                          |
| `.remove_file()`    | Removes a file of the name given if any exists. Note that a file should only be removed when sure that all other requests using the file are completed. If you delete a file right after a request you run the risk of it removing the file before the task could be run and causing a server crash (`Request`'s go after `Notification`'s and `Ping`'s). | `filename`: str                                                                                                                                                                                                                                                                                                            |
| `.kill_IPC()`       | This kills the IPC process and acts as a precaution against wasted CPU when the main thread no longer needs the IPC                                                                                                                                                                                                                                       | None                                                                                                                                                                                                                                                                                                                       |

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

    context.request(
        "highlight", file="test", language="python", text_range=(1, 30)
    )

    sleep(1)
    output: Response | None = context.get_response("highlight")
    print(output["result"])  # type: ignore
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
