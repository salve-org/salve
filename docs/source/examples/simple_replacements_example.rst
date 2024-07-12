===========================
Simple Replacements Example
===========================

.. code-block:: python

    from time import sleep
    
    from salve_ipc import IPC, REPLACEMENTS, Response
    
    
    def main():
        context = IPC()
    
        context.update_file(
            "test",
            open(__file__, "r+").read(),
        )
    
        context.request(
            REPLACEMENTS,
            file="test",
            expected_keywords=[],
            current_word="contest",
        )
    
        sleep(1)
        output: Response | None = context.get_response(REPLACEMENTS)
        print(output)
        context.kill_IPC()
    
    
    if __name__ == "__main__":
        main()

See the file example file `here <https://github.com/Moosems/salve/blob/master/examples/simple_replacements_example.py>`_.