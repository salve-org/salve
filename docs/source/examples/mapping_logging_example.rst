=======================
Mapping Logging Example
=======================

.. code-block:: python

    from logging import INFO, Logger, basicConfig, getLogger
    from time import sleep
    
    from salve_dependency_hub import conversion_dict
    from tree_sitter import Language, Parser, Tree
    
    from salve import HIGHLIGHT, IPC, Token, make_unrefined_mapping
    
    basicConfig(
        level=INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logger: Logger = getLogger("Main")
    
    
    def main():
        context = IPC()
    
        code: str = open(__file__, "r+").read()
    
        context.update_file("test", code)
    
        # Run normally to get the normal Tokens as a cross reference
        # NOTE: if you try running the tree sitter higlighter without a mapping it just returns the
        # pygments tokens assuming you will create a mapping with it. wWe aren't here but its good
        # to know
        context.request(HIGHLIGHT, file="test", language="python")
    
        sleep(1)
    
        pygments_output: list[Token] = context.get_response(HIGHLIGHT)["result"]  # type: ignore
    
        # Not a comprehensive list but it works for this example
        avoid_types = [
            "class_definition",
            "block",
            "function_definition",
            "if_statement",
            "expression_statement",
            "call",
            "parameters",
            "argument_list",
            "module",
            "type",
        ]
    
        tree: Tree = Parser(Language(conversion_dict["python"]())).parse(
            bytes(code, "utf8")
        )
    
        print(
            make_unrefined_mapping(
                tree, pygments_output, avoid_types, logger=logger
            )
        )
    
        context.kill_IPC()
    
    
    if __name__ == "__main__":
        main()

See the file example file `here <https://github.com/salve-org/salve/blob/master/examples/mapping_logging_example.py>`_.