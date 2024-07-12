=============
Example Usage
=============

.. code-block:: python

    from os import set_blocking
    from selectors import EVENT_READ, DefaultSelector
    from sys import stdin, stdout
    
    from salve_ipc import AUTOCOMPLETE, IPC, Response
    
    
    def main():
        # Create context for IPC
        context = IPC()
    
        # Allow for nice input
        set_blocking(stdin.fileno(), False)
        set_blocking(stdin.fileno(), False)
        selector = DefaultSelector()
        selector.register(stdin, EVENT_READ)
    
        # Print out "Code: "
        stdout.write("Code: \n")
        stdout.flush()
    
        while True:
            # Check input
            events = selector.select(0.025)
            if events:
                # Make requests
                for line in stdin:
                    # Update file
                    context.update_file("test", line)
    
                    # Make request to server
                    context.request(
                        AUTOCOMPLETE,
                        expected_keywords=[],
                        file="test",
                        current_word=line[-2],
                    )
    
            # Check output
            # context.cancel_request("autocomplete") # Uncommenting this line will cause the request to always be cancelled
            output: Response | None = context.get_response(AUTOCOMPLETE)
            if not output:
                continue
    
            # Write response
            stdout.write(str(output) + "\n")
            stdout.flush()
    
        context.kill_IPC()
    
    
    if __name__ == "__main__":
        main()

See the file example file `here <https://github.com/Moosems/salve/blob/master/examples/example_usage.py>`_.