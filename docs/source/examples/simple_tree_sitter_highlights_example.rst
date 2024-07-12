=====================================
Simple Tree Sitter Highlights Example
=====================================

.. code-block:: python

    from time import sleep
    
    from salve_dependency_hub import conversion_dict
    
    from salve import HIGHLIGHT_TREE_SITTER, IPC, Response
    
    
    def main():
        context = IPC()
    
        context.update_file(
            "test",
            open(__file__, "r+").read(),
        )
    
        # See simple_mapping_example.py for an example how to make these
        # This example is not comprehensive by any means and was made specifically for this kind of input
        example_mapping: dict[str, str] = {
            "class": "Keyword",
            "identifier": "Name",
            ":": "Punctuation",
            "def": "Keyword",
            "(": "Punctuation",
            ")": "Punctuation",
            "{": "Punctuation",
            "}": "Punctuation",
            "[": "Punctuation",
            "]": "Punctuation",
            "|": "Punctuation",
            "==": "Punctuation",
            "->": "Operator",
            "none": "Keyword",
            "if": "Keyword",
            "string_start": "String",
            "string_content": "String",
            "string_end": "String",
            "string": "String",
            ".": "Punctuation",
            ",": "Punctuation",
            "=": "Punctuation",
            "integer": "Number",
            "comment": "Comment",
            "import": "Keyword",
            "from": "Keyword",
        }
    
        context.request(
            HIGHLIGHT_TREE_SITTER,
            file="test",
            language="python",
            text_range=(1, 30),
            tree_sitter_language=conversion_dict["python"],
            mapping=example_mapping,
        )
    
        sleep(1)
        output: Response | None = context.get_response(HIGHLIGHT_TREE_SITTER)
        print(output)
        context.kill_IPC()
    
    
    if __name__ == "__main__":
        main()

See the file example file `here <https://github.com/Moosems/salve/blob/master/examples/simple_tree_sitter_highlights_example.py>`_.