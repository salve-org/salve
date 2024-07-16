=====================================
Simple Tree Sitter Highlights Example
=====================================

.. code-block:: python

    from time import sleep
    
    from salve_dependency_hub import langauge_mappings, language_functions
    
    from salve import HIGHLIGHT_TREE_SITTER, IPC, Response
    
    
    def main():
        context = IPC()
    
        context.update_file(
            "test",
            open(__file__, "r+").read(),
        )
    
        context.request(
            HIGHLIGHT_TREE_SITTER,
            file="test",
            language="python",
            text_range=(1, 30),
            tree_sitter_language=language_functions["python"],
            mapping=langauge_mappings["python"],
        )
    
        sleep(1)
        output: Response | None = context.get_response(HIGHLIGHT_TREE_SITTER)
        print(output)
        context.kill_IPC()
    
    
    if __name__ == "__main__":
        main()

See the file example file `here <https://github.com/Moosems/salve/blob/master/examples/simple_tree_sitter_highlights_example.py>`_.