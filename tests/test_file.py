from this import s  # noqa: F401

Bar = int  # alias


class Foo(Bar):
    def __init__(self):
        pass


Foo()
# https://www.google.com
