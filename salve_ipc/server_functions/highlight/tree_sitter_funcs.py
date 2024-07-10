from tree_sitter import Node, Parser, Tree, TreeCursor

from salve_ipc import Token
from salve_ipc.server_functions.highlight.tokens import merge_tokens


def node_to_tokens(root_node: Tree, mapping: dict[str, str]) -> list[Token]:
    cursor: TreeCursor = root_node.walk()
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


def edit_tree(
    old_code: str, new_code: str, tree: Tree, parser: Parser
) -> Tree:
    # NOTE: Made with Chat GPT, don't have any idea why or how it works, but it does :D
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


# Given a test token from the mapping function it will try to match it with the
# closest token type found elsewhere in the pygments list
def token_type_of_test(test_token: Token, pygments_tokens: list[Token]) -> str:
    if not pygments_tokens:
        return ""

    for new_token in pygments_tokens:
        # Check if the tokens are effectively the same
        same_line: bool = test_token[0][0] == new_token[0][0]
        same_col_and_length: bool = (
            test_token[0][1] == new_token[0][1]
            and test_token[1] == new_token[1]
        )
        if not same_line:
            continue
        if same_line and same_col_and_length:
            return new_token[2]

        # Check if the token's range is covered by the new_token
        old_token_end: int = test_token[0][1] + test_token[1]
        new_token_end: int = new_token[0][1] + new_token[1]

        fully_contained: bool = (
            old_token_end <= new_token_end
            and test_token[0][1] >= new_token[0][1]
        )

        # We assume there is no partial overlap
        if fully_contained:
            return new_token[2]

    return ""


# NOTE: The auto-mapper is great for users who don't want to spend forever mapping stuff so it
# will give a mapping made from what context it can get and then the user can refine it further
def make_unrefined_mapping(
    root_node: Tree,
    pygments_special_output: list[Token],
    avoid_list: list[str],
) -> dict[str, str]:
    # We assume that the pygments special output has parsed this the
    cursor: TreeCursor = root_node.walk()
    mapping: dict[str, str] = {}
    visited_nodes: set = set()

    while True:
        node: Node | None = cursor.node
        if not node:
            break

        # Avoid re-processing the same node
        if node.id not in visited_nodes:
            visited_nodes.add(node.id)

            if node.type in mapping or node.type in avoid_list:
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
