<h1 align="center">Salve v1.1.0</h1>

# Installation

In the Command Line, paste the following: `pip install salve`

## Description

Salve is an IPC library that can be used by code editors to easily get autocompletions, replacements, editorconfig suggestions, definitions, and syntax highlighting.

> **Notes:**
>  - Due to the way Windows handles chars the hidden character highlighter may not work properly. See [#57](https://github.com/salve-org/salve/pull/57). If anyone knows how to fix this, I would greatly appreciate you opening a PR :)

## Documentation

You can now read the official documentation for Salve [here](https://salve.readthedocs.io/en/latest/) on ReadTheDocs. I worked fairly hard on making it look good and be legible but if you notice typos don't hesitate to open an issue or make a PR.

## Contributing

To contribute, fork the repository, make your changes, and then make a pull request. If you want to add a feature, please open an issue first so it can be discussed. Note that whenever and wherever possible you should try to use stdlib modules rather than external ones.

## Required Python Version: 3.11+

Salve will use the three most recent versions (full releases) going forward and will drop any older versions as new ones come out. This is because I hope to keep this package up to date with modern python versions as they come out instead of being forced to maintain decade old python versions.
Currently 3.11 is the minimum (instead of 3.10) as Salve was developed under 3.12 and there are many features that Salve IPC relies on from this version I want. However, after 3.14 is released, the minimum version will be 3.12 (as would be expected from the plan) and will change accordingly in the future as is described in the plan above.

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE).
