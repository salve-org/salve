from this import s  # noqa: F401

Bar: type = int
(xyz := test)  # noqa: F821

print()


class Foo(Bar):
    """
    test
    """

    def __init__(self):
        pass


Foo()
# https://www.google.com
"""
test
"""
