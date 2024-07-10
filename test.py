from tree_sitter import Language, Node, Parser, Tree, TreeCursor
from tree_sitter_python import language as py_language

from salve_ipc import Token
from salve_ipc.server_functions.highlight.tokens import (
    merge_tokens,
)

original_code_snippet: str = """class foo:
    def bar() -> None:
        if baz:
            qux()
"""
parser: Parser = Parser(
    Language(py_language())
)  # Will be input along with code snippet

tree = parser.parse(bytes(original_code_snippet, "utf8"))
# good_python_generic_mapping: dict[str, str] = {
#     "class": "Keyword",
#     "identifier": "Name",
#     ":": "Punctuation",
#     "def": "Keyword",
#     "(": "Punctuation",
#     ")": "Punctuation",
#     "->": "Operator",
#     "none": "Keyword",
#     "if": "Keyword",
#     "string_start": "String",
#     "string_content": "String",
#     "string_end": "String",
#     "string": "String",
#     "integer": "Number",
#     "print": "Name",
# }

# A minimal generic mapping for python
python_generic_mapping: dict[str, str] = {
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


def traverse_node(root_node: Tree, mapping: dict[str, str]) -> list[Token]:
    cursor: TreeCursor = tree.walk()
    tokens: list[Token] = []
    visited_nodes: set = set()

    while True:
        node: Node | None = cursor.node
        if not node:
            break

        # Avoid re-processing the same node
        if node.id not in visited_nodes:
            visited_nodes.add(node.id)

            if node.child_count == 0:
                # Avoid KeyError (should probably ask for a logger)
                if node.type not in mapping:
                    print("---")
                    print("NODE TOKEN NOT MAPPED")
                    print(node.type, node.start_point, node.end_point)
                    continue

                token = (
                    (node.start_point[0] + 1, node.start_point[1]),
                    node.end_point[1] - node.start_point[1],
                    mapping[node.type],
                )
                tokens.append(token)

        # Another child!
        if cursor.goto_first_child():
            continue

        # A sibling node!
        if cursor.goto_next_sibling():
            continue

        # Go up to parent to look for siblings and possibly other children (this is a depth first search)
        while cursor.goto_parent():
            if cursor.goto_next_sibling():
                break
        else:
            break

    return merge_tokens(tokens)


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
tree_sitter_output = traverse_node(tree, mapping=python_generic_mapping)
assert own_output == tree_sitter_output


def edit_tree(old_code: str, new_code: str, tree: Tree) -> Tree:
    """Made with Chat GPT, don't have any idea why or how it works, but it does :D"""
    if old_code == new_code:
        return tree

    old_lines = old_code.splitlines(keepends=True)
    new_lines = new_code.splitlines(keepends=True)

    # Find the first differing line
    def find_first_diff(old_lines, new_lines):
        min_len = min(len(old_lines), len(new_lines))
        for i in range(min_len):
            if old_lines[i] != new_lines[i]:
                return i
        return min_len

    # Find the last differing line
    def find_last_diff(old_lines, new_lines):
        min_len = min(len(old_lines), len(new_lines))
        for i in range(1, min_len + 1):
            if old_lines[-i] != new_lines[-i]:
                return len(old_lines) - i
        return min_len

    # Get line diffs
    first_diff = find_first_diff(old_lines, new_lines)
    last_diff_old = find_last_diff(old_lines, new_lines)
    last_diff_new = find_last_diff(new_lines, old_lines)

    # Calculate byte offsets
    start_byte = sum(len(line) + 1 for line in old_lines[:first_diff])
    old_end_byte = sum(
        len(line) + 1 for line in old_lines[: last_diff_old + 1]
    )
    new_end_byte = sum(
        len(line) + 1 for line in new_lines[: last_diff_new + 1]
    )

    # Edit the tree
    tree.edit(
        start_byte=start_byte,
        old_end_byte=old_end_byte,
        new_end_byte=new_end_byte,
        start_point=(first_diff, 0),
        old_end_point=(
            last_diff_old,
            len(old_lines[last_diff_old]) if old_lines else 0,
        ),
        new_end_point=(
            last_diff_new,
            len(new_lines[last_diff_new]) if new_lines else 0,
        ),
    )

    # Reparse the tree from the start_byte
    tree = parser.parse(bytes(new_code, "utf8"), tree)

    return tree


tree: Tree = edit_tree(original_code_snippet, original_code_snippet, tree)

old_code = original_code_snippet
code_snippet = '"""' + original_code_snippet + '"""'

tree: Tree = edit_tree(old_code, code_snippet, tree)
print(traverse_node(tree, mapping=python_generic_mapping))

old_code = code_snippet
code_snippet = code_snippet[3 : len(code_snippet) - 3]
code_snippet += 'print("Boo!")'

tree: Tree = edit_tree(old_code, code_snippet, tree)
output = traverse_node(tree, mapping=python_generic_mapping)

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


def token_type_of_test(old_token: Token, new_tokens: list[Token]) -> str:
    if not new_tokens:
        return ""

    for new_token in new_tokens:
        # Check if the tokens are effectively the same
        same_line: bool = old_token[0][0] == new_token[0][0]
        same_col_and_length: bool = (
            old_token[0][1] == new_token[0][1] and old_token[1] == new_token[1]
        )
        if not same_line:
            continue
        if same_line and same_col_and_length:
            return new_token[2]

        # Check if the token's range is covered by the new_token
        old_token_end: int = old_token[0][1] + old_token[1]
        new_token_end: int = new_token[0][1] + new_token[1]

        fully_contained: bool = (
            old_token_end <= new_token_end
            and old_token[0][1] >= new_token[0][1]
        )

        # We assume there is no partial overlap
        if fully_contained:
            return new_token[2]

    return ""


def make_unrefined_mapping(
    root_node: Tree,
    pygments_special_output: list[Token],
    avoid_list: list[str],
) -> dict[str, str]:
    # We assume that the pygments special output has parsed this the
    cursor: TreeCursor = tree.walk()
    mapping: dict[str, str] = {}
    visited_nodes: set = set()

    while True:
        node: Node | None = cursor.node
        if not node:
            break

        # Avoid re-processing the same node
        if node.id not in visited_nodes:
            visited_nodes.add(node.id)

            if node.type in mapping or node.type in avoid_types:
                continue

            temp_token: Token = (
                (node.start_point[0] + 1, node.start_point[1]),
                node.end_point[1] - node.start_point[1],
                "TEST",
            )
            token_type = token_type_of_test(
                temp_token, pygments_special_output
            )
            if not token_type:
                print(
                    f"CANNOT MAP: node.type: {node.type}, node temp_token: {temp_token}"
                )

            mapping[node.type] = token_type

        # Another child!
        if cursor.goto_first_child():
            continue

        # A sibling node!
        if cursor.goto_next_sibling():
            continue

        # Go up to parent to look for siblings and possibly other children (this is a depth first search)
        while cursor.goto_parent():
            if cursor.goto_next_sibling():
                break
        else:
            break

    return mapping


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
assert (
    make_unrefined_mapping(
        tree,
        code_snippet_output,
        avoid_types,
    )
    == python_generic_mapping
)
