from tree_sitter import Language, Parser, Tree
from tree_sitter_python import (
    language as py_language,  # Downloaded automatically by test runners
)

from salve_ipc import make_unrefined_mapping
from salve_ipc.server_functions.highlight.tree_sitter_funcs import (
    edit_tree,
    node_to_tokens,
    tree_sitter_highlight,
)

# Create useful variables
original_code_snippet: str = """class foo:
    def bar() -> None:
        if baz:
            qux()
"""
minimal_python_mapping: dict[str, str] = {
    "class": "Keyword",
    "identifier": "Name",
    ":": "Punctuation",
    "def": "Keyword",
    "(": "Punctuation",
    ")": "Punctuation",
    "->": "Operator",
    "none": "Keyword",
    "if": "Keyword",
    "string_start": "String",
    "string_content": "String",
    "string_end": "String",
    "string": "String",
}
pygments_output = [
    ((1, 0), 5, "Keyword"),
    ((1, 6), 3, "Name"),
    ((1, 9), 1, "Punctuation"),
    ((2, 4), 3, "Keyword"),
    ((2, 8), 3, "Name"),
    ((2, 11), 2, "Punctuation"),
    ((2, 14), 2, "Operator"),
    ((2, 17), 4, "Keyword"),
    ((2, 21), 1, "Punctuation"),
    ((3, 8), 2, "Keyword"),
    ((3, 11), 3, "Name"),
    ((3, 14), 1, "Punctuation"),
    ((4, 12), 3, "Name"),
    ((4, 15), 2, "Punctuation"),
]
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
code_snippet_output = [
    ((1, 0), 5, "Keyword"),
    ((1, 6), 3, "Name"),
    ((1, 9), 1, "Punctuation"),
    ((2, 4), 3, "Keyword"),
    ((2, 8), 3, "Name"),
    ((2, 11), 2, "Punctuation"),
    ((2, 14), 2, "Operator"),
    ((2, 17), 4, "Keyword"),
    ((2, 21), 1, "Punctuation"),
    ((3, 8), 2, "Keyword"),
    ((3, 11), 3, "Name"),
    ((3, 14), 1, "Punctuation"),
    ((4, 12), 3, "Name"),
    ((4, 15), 2, "Punctuation"),
    ((5, 0), 5, "Name"),
    ((5, 5), 1, "Punctuation"),
    ((5, 6), 6, "String"),
    ((5, 12), 1, "Punctuation"),
]
parser: Parser = Parser(
    Language(py_language())
)  # Will be input along with code snippet


def test_tree_sitter_highlight():
    assert (
        tree_sitter_highlight(
            original_code_snippet, "python", minimal_python_mapping, parser
        )
        == pygments_output
    )

    # Run a second time to ensure the tree updates properly
    code_snippet = original_code_snippet + 'print("Boo!")'
    assert (
        tree_sitter_highlight(code_snippet, "python", minimal_python_mapping)
        == code_snippet_output
    )

def test_make_mapping():
    code_snippet = original_code_snippet + 'print("Boo!")'
    tree: Tree = parser.parse(bytes(code_snippet, "utf8"))
    assert (
        make_unrefined_mapping(
            tree,
            code_snippet_output,
            avoid_types,
        )
        == minimal_python_mapping
    )


def test_edit_tree():
    tree = parser.parse(bytes(original_code_snippet, "utf8"))

    tree_sitter_output = node_to_tokens(tree, mapping=minimal_python_mapping)
    assert pygments_output == tree_sitter_output

    assert (
        edit_tree(original_code_snippet, original_code_snippet, tree, parser)
        == tree
    )

    old_code = original_code_snippet
    code_snippet = '"""' + original_code_snippet + '"""'
    tree: Tree = edit_tree(old_code, code_snippet, tree, parser)
    assert node_to_tokens(tree, mapping=minimal_python_mapping) == [
        ((1, 0), 0, "String"),
        ((5, 0), 3, "String"),
    ]

    old_code = code_snippet
    code_snippet = original_code_snippet + 'print("Boo!")'
    tree: Tree = edit_tree(old_code, code_snippet, tree, parser)
    output = node_to_tokens(tree, mapping=minimal_python_mapping)

    assert output == [
        ((1, 0), 5, "Keyword"),
        ((1, 6), 3, "Name"),
        ((1, 9), 1, "Punctuation"),
        ((2, 4), 3, "Keyword"),
        ((2, 8), 3, "Name"),
        ((2, 11), 2, "Punctuation"),
        ((2, 14), 2, "Operator"),
        ((2, 17), 4, "Keyword"),
        ((2, 21), 1, "Punctuation"),
        ((3, 8), 2, "Keyword"),
        ((3, 11), 3, "Name"),
        ((3, 14), 1, "Punctuation"),
        ((4, 12), 3, "Name"),
        ((4, 15), 2, "Punctuation"),
        ((5, 0), 5, "Name"),
        ((5, 5), 1, "Punctuation"),
        ((5, 6), 6, "String"),
        ((5, 12), 1, "Punctuation"),
    ]


if __name__ == "__main__":
    test_edit_tree()
