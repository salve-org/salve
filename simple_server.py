from tkinter import Entry, Label

random_list = ["apples", "oranges", "bananas"]
times_accessed = 0


def get_item(index: str) -> str:
    global times_accessed
    times_accessed += 1

    try:
        intdex = int(index)
    except ValueError:
        return "?"

    try:
        return str(random_list[intdex])
    except IndexError:
        return "?"
