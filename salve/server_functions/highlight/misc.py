def normal_text_range(
    full_text: str, text_range: tuple[int, int] = (1, -1)
) -> tuple[list[str], tuple[int, int]]:
    split_text: list[str] = full_text.splitlines()

    if text_range[1] == -1:
        # This indicates that the text range should span the length of the entire code
        text_range = (text_range[0], len(split_text))

    # We want only the lines in the text range because this list is iterated
    split_text = split_text[text_range[0] - 1 : text_range[1]]

    return (split_text, text_range)
