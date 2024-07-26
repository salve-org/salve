=============
Example Usage
=============

Now that you have ``Salve`` installed, let's try running a simple example that prints out the highlight ``Token``'s of the file being run:

.. code-block:: python

    from time import sleep

    # We import the IPC class, the HIGHLIGHT command, and the Response TypedDict
    # NOTE: The HIGHLIGHT variable is actually just a string that makes it easier to get
    # spell checking from your code editor
    from salve import HIGHLIGHT, IPC, Response


    def main():

        # Here we define the context (which creates the other process).
        context = IPC()

        # In order to actually use a file, we need to update the internal file system
        # which is done by IPC.update_file(). Note that nothing prevents you, the
        # user, from using arbitrary code snippets instead of real files.
        context.update_file(
            "test", # Name the file for the system
            open(__file__, "r+").read(), # Give the contents as a string
        )

        # Next, we request the system to make syntax highlights. If you want it to
        # highlight the whole file given , just leave the text_range argument unspecified
        context.request(
            HIGHLIGHT, file="test", language="python", text_range=(1, 30)
        )

        # Letting the other process spin up and create syntax highlights
        sleep(1)

        # If there is no response we give None instead of raising an Exception
        output: Response | None = context.get_response(HIGHLIGHT)
        print(output)

        # Finally, if you are done with the IPC before the rest of the program, you can
        # kill it to save a bit of CPU time.
        context.kill_IPC()


    # Because this module is made with multiprocessing we need an if __name__ == "__main__" clause
    if __name__ == "__main__":
        main()

Now thats all fine and dandy, but what about if I need it to work for [insert random use case here]? Well, ``Salve`` is actually meant to be super flexible so if you use it properly, it can elegantly fit nearly any use case. For example, what if you need it to fit a tkinter application that uses an event loop? Well, take a look:

.. code-block:: python

    from salve import IPC, Response, HIGHLIGHT
    from tkinter import Tk

    class App(Tk):
        def __init__(self) -> None:
            Tk.__init__(self)

            # When we first create an IPC object, it takes a while to load (not on the main thread)
            # while the second process is created.
            self.context = IPC()

            # At some point something calls the request_highlight function
            # In a real application we would also define a callback to send the
            # output to
            self.after(500, lambda: self.request_highlight(open(__file__, "r+").read()))

            self.output: Response | None = None

            self.mainloop()

        def request_highlight(self, code: str) -> None:
            self.output = None
            self.context.update_file("foo", code)
            self.context.request(HIGHLIGHT, file="foo", language="python")
            self.after(50, self.check_output)

        def check_output(self) -> None:
            if (output := self.context.get_response(HIGHLIGHT)):
                self.output = output
                print(self.output)
                return
            self.after(50, self.check_output)

    if __name__ == "__main__":
        App()

Some quick notes to remember as you use ``Salve``:

- The first time that the system is loaded or a new server needs to be started it will take a fair bit longer as a new interpreter needs to be created.
- Any usage of ``IPC`` needs to have been called from an ``if __name__ == "__main__":`` block to prevent a multiproccesing error.

.. |br| raw:: html

   <br />

|br|

Of course, you can do far more with ``Salve`` than just getting syntax highlights. For example: what if you want to get autocompletions? Well, there is of course the the :doc:`command-sheet`.
