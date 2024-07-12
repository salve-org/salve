========================
Simple Highlight Example
========================

.. code-block:: python

    from time import sleep
    
    from salve_ipc import HIGHLIGHT, IPC, Response
    
    
    def main():
        context = IPC()
    
        context.update_file(
            "test",
            open(__file__, "r+").read() * 20,
        )
    
        context.request(
            HIGHLIGHT, file="test", language="python", text_range=(1, 30)
        )
    
        sleep(1)
        output: Response | None = context.get_response(HIGHLIGHT)
        print(output)
        context.kill_IPC()
    
    
    if __name__ == "__main__":
        main()

See the file example file `here <https://github.com/Moosems/salve/blob/master/examples/simple_highlight_example.py>`_.