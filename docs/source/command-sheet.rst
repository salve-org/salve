=============
Command Sheet
=============

Below is a chart outlining the different request commands you can give and the different arguments they require with an explanation in parentheses if needed.

.. list-table:: **Requestable Commands**
    :widths: 25 75
    :header-rows: 1

    * - Command
      - arguments
    * - ``AUTOCOMPLETE``
      - file: ``str``,

        current_word: ``str`` (the portion of the word being typed),

        expected_keywords: ``list[str]`` (any special keywords for the language (optional))
    * - ``REPLACEMENTS``
      - file: ``str``,

        current_word: ``str`` (the word needing to be replaced),

        expected_keywords: ``list[str]`` (any special keywords for the language (optional))
    * - ``HIGHLIGHT``
      - file: ``str``,

        language: ``str``,

        text_range: ``tuple[int, int]`` (the lower and upper line bounds (inclusively) of what text to highlight (optional))
    * - ``EDITORCONFIG``
      - file_path: ``pathlib.Path | str`` (the absolute path to the file you need the editorconfig data on),
    * - ``DEFINITION``
      - file: ``str``,

        current_word: ``str`` (the word being searched for),

        definition_starters: ``list[tuple[str, str]]`` (list of regexes to search for and a string associated (see :doc:`examples/simple_definitions_example`))
    * - ``HIGHLIGHT_TREE_SITTER``
      - file: ``str``,

        language: ``str``,

        text_range: ``tuple[int, int]`` (see HIGHLIGHT explanation),

        tree_sitter_language: ``Callable | pathlib.Path | str`` (should be salve_dependency_hub.language() (see :ref:`Extra Tools <Salve Dependency Hub Overview>`) or a Path/str that points to a .so file) (this argument is optional after the first highlight if you've used that language before),

        mapping: ``dict[str, str]`` (Tree Sitter token to desired ``Token`` type mapping)

To see how to use any given one of these in more detail, visit the :doc:`examples` page! Otherwise move on to the :doc:`special-classes` page instead.
