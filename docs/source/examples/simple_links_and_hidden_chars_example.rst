=====================================
Simple Links And Hidden Chars Example
=====================================

.. code-block:: python

    from time import sleep
    
    from salve import LINKS_AND_CHARS, IPC, Response
    
    
    def main():
        context = IPC()
    
        context.update_file(
            "test",
            open(__file__, "r+").read(),
        )
    
        context.request(
            LINKS_AND_CHARS, file="test", text_range=(1, 30)
        )
    
        sleep(1)
        output: Response | None = context.get_response(LINKS_AND_CHARS)
        print(output)
        context.kill_IPC()
    
    
    if __name__ == "__main__":
        main()

See the file example file `here <https://github.com/salve-org/salve/blob/master/examples/simple_links_and_hidden_chars_example.py>`_.