=============
Example Usage
=============

Now that you have ``Salve`` installed, let's try running a simple example that prints out the highlight ``Token``'s of the file being run:

.. code-block:: python

    from time import sleep

    # We import the IPC class, the HIGHLIGHT command, and the Response TypedDict
    # NOTE: The HIGHLIGHT is actually just a string but it makes it easier to get
    # spelling errors from your code editor
    from salve import HIGHLIGHT, IPC, Response


    # Because this module is made with multiprocessing we need any usage to
    # initially be called from an if __name__ == "__main__" clause
    def main():

        # Here we define the context (create the other process) nothing more. IPC
        # doesn't take any arguments, it just sets itself up for you!
        context = IPC()

        # In order to actually use a file, we need to update the internal system
        # which is done by IPC.update_file(). As promised, this system is also highly
        # powerful and flexible and because of this nothign prevents you, the user,
        # from using arbitrary code snippets instead of real files.
        context.update_file(
            "test", # Name the file for the system
            open(__file__, "r+").read(), # Give the contents as a string
        )

        # Next, we request the system to make highlights (using the HIGHLIGHT)
        # command, tell it to use the file "test", that it should be highlighting
        # for a python file, and to only return the code in lines 1-30. If you
        # want it to highlight the whole file given , just leave the argument
        # empty (unspecified)
        context.request(
            HIGHLIGHT, file="test", language="python", text_range=(1, 30)
        )

        # It doesn't actually take a full second to get highlights but its simpler
        # for the example to just do this.
        sleep(1)

        # The reason you need a union of Response and None is because we choose to
        # give None when yo ask for the highlight of something that hasn't had a server
        # response rather than raise an exception.
        output: Response | None = context.get_response(HIGHLIGHT)
        print(output)

        # Finally, if you are done with the IPC before the rest of the program, you can
        # kill it like so. It automatically dies when the main thread dies but this lets
        # you save a bit of CPU usage
        context.kill_IPC()


    if __name__ == "__main__":
        main()

Now I know thats a lot of comments, it is, but it also explains everything in a lot of detail.

In a more realistic case, you would probably do something more like the following:

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

Befor you leave, here are some quick reminders to remember as you use ``Salve``:

- The first time that the system is loaded or a new server needs to be started it will take a fair bit longer.
- Any usage of ``IPC ``needs to originally have been called from an ``if __name__ == "__main__":`` block to prevent a multiproccesing error.

.. |br| raw:: html

   <br />

|br|

Now that is one beautiful application! Of course, there is far more that you can do beyond just getting highlights. For example: what if you want to get autocompletions? Well, there is of course the the handy :doc:`command-sheet` page.
