from salve.server_functions.highlight.tokens import overwrite_tokens


def test_overwrite_tokens():
    assert overwrite_tokens(
        [((1, 0), 3, "TEST1")], [((1, 2), 3, "TEST2")]
    ) == [
        ((1, 0), 2, "TEST1"),
        ((1, 2), 3, "TEST2"),
    ]
    assert overwrite_tokens(
        [((1, 0), 1, "TEST1")], [((1, 2), 3, "TEST2")]
    ) == [
        ((1, 0), 1, "TEST1"),
        ((1, 2), 3, "TEST2"),
    ]
    assert overwrite_tokens(
        [((1, 4), 5, "TEST1")], [((1, 2), 3, "TEST2")]
    ) == [
        ((1, 2), 3, "TEST2"),
        ((1, 5), 4, "TEST1"),
    ]
    assert overwrite_tokens(
        [((1, 3), 1, "TEST1")], [((1, 2), 3, "TEST2")]
    ) == [((1, 2), 3, "TEST2")]
    assert overwrite_tokens(
        [((1, 0), 9, "TEST1")], [((1, 2), 3, "TEST2")]
    ) == [
        ((1, 0), 2, "TEST1"),
        ((1, 2), 3, "TEST2"),
        ((1, 5), 4, "TEST1"),
    ]
    assert overwrite_tokens(
        [((1, 0), 9, "TEST1"), ((1, 11), 2, "TEST3")],
        [((1, 2), 3, "TEST2"), ((1, 12), 3, "TEST4")],
    ) == [
        ((1, 0), 2, "TEST1"),
        ((1, 2), 3, "TEST2"),
        ((1, 5), 4, "TEST1"),
        ((1, 11), 1, "TEST3"),
        ((1, 12), 3, "TEST4"),
    ]
