<h1 align="center">Salve</h1>

> **Note**
> This package does not work on Windows machines as `Selector.select()` does not work on them.

# Installation

In the Command Line, paste the following: `pip install salve_ipc` (NOT YET WORKING).

## Description

Salve is an IPC library that can be used by code editors to get autocomplete and, in the future, syntax highlighting.

## Documentation

### `IPC` Class

| Method    | Description                                                                                                                                              | Arguments |
| --------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- |
| `.ping()` | Pings the server. After five seconds the server closes if not pinged so it is better for performance to keep it alive but it will be reopened either way | None      |

| `.get_response()` | Gets a response of the requested command | `command`: str |
| `.request()` | Makes a request to the server |`command`: str, `expected_keywords`: list[str], `file`: str, `current_word`: str |
| `.update_file()`| Updates files stored on the server that are used to get responses |`filename`: str, `current_state`: str (just the text of the file) |
| `.remove_file()`| Removes a file of the name given if any exists |`filename`: str |
| `.kill_IPC()` | This kills the IPC process and acts as a precaution against wasted CPU when the main thread no longver needs the IPC | None |

### Basic Usage:

```python
from os import set_blocking
from selectors import EVENT_READ, DefaultSelector
from sys import stdin, stdout

from salve_ipc import IPC, Response

autocompleter = IPC()

set_blocking(stdin.fileno(), False)
set_blocking(stdin.fileno(), False)
selector = DefaultSelector()
selector.register(stdin, EVENT_READ)

stdout.write("Code: \n")
stdout.flush()

while True:
    # Keep IPC alive
    autocompleter.ping()

    # Add file
    autocompleter.add_file("test", "")

    # Check input
    events = selector.select(0.025)
    if events:
        # Make requests
        for line in stdin:
            autocompleter.update_file("test", line)
            autocompleter.request(
                "autocomplete",
                expected_keywords=[],
                full_text=line,
                current_word=line[-2],
            )

    # Check output
    output: Response | None = autocompleter.get_response()
    if not output:
        continue
    stdout.write(str(output) + "\n")
    stdout.flush()
```

## How to run and contribute

### Running

To run the example, move `examples/example_usage.py` to the root directory and run with python. The project uses only standard library modules, so there are no external dependencies.

To test newer features or test code in a Pull Review, do the same but move it back after if you plan to make a PR.

### Contributing

To contribute, fork the repository, make your changes, and then make a pull request. If you want to add a feature, please open an issue first so we can discuss it.

## License

This project is licensed under the MIT License - see the [LICENSE](./LISCENSE).
