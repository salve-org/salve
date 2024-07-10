from tree_sitter import Language, Node, Parser
from tree_sitter_python import language

from salve_ipc import Token
from salve_ipc.server_functions.highlight.tokens import merge_tokens

PY_LANGUAGE = Language(language())
print(PY_LANGUAGE)
parser = Parser(PY_LANGUAGE)
code_snippet: str = """class foo:
    def bar() -> None:
        if baz:
            qux()
"""
tree = parser.parse(bytes(code_snippet, "utf8"))
tree_sitter_to_generic_mapping = {
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
    "integer": "Number",
    "print": "Name",
}


def traverse_node(node: Node) -> list[Token]:
    output_tokens: list[Token] = []
    if node.children:
        for child in node.children:
            output = traverse_node(child)
            for token in output:
                output_tokens.append(token)
        output_tokens = merge_tokens(output_tokens)
        return output_tokens

    if node.grammar_name not in tree_sitter_to_generic_mapping:
        print("---")
        print("NODE TOKEN NOT MAPPED")
        print(node.type, node.start_point, node.end_point, node.walk)
        return output_tokens

    token: Token = (
        (node.start_point.row + 1, node.start_point.column),
        node.end_point.column - node.start_point.column,
        tree_sitter_to_generic_mapping[node.type],
    )
    output_tokens.append(token)
    output_tokens = merge_tokens(output_tokens)
    return output_tokens


own_output = [
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
print(traverse_node(tree.root_node))
tree_sitter_output = traverse_node(tree.root_node)

print(own_output == tree_sitter_output)
