from time import sleep

from tree_sitter import Language, Parser, Tree
from tree_sitter_python import language

from salve_ipc import (
    HIGHLIGHT,
    IPC,
    Token,
    make_unrefined_mapping,
)


def main():
    context = IPC()

    code: str = open(__file__, "r+").read()

    context.update_file("test", code)

    # Run once without a mapping first so the system adds the lanugage for when mapping
    context.request(HIGHLIGHT, file="test", language="python")

    sleep(1)
    # Note that when you try running the tree sitter higlighter without a mapping it just returns the
    # pygments tokens assuming you will create a mapping with it
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

    tree: Tree = Parser(Language(language())).parse(bytes(code, "utf8"))

    print(
        make_unrefined_mapping(
            tree,
            pygments_output,
            avoid_types,
        )
    )

    context.kill_IPC()


if __name__ == "__main__":
    main()
