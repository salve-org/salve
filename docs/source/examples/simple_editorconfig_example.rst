===========================
Simple Editorconfig Example
===========================

.. code-block:: python

    from time import sleep
    
    from salve import EDITORCONFIG, IPC, Response
    
    
    def main():
        context = IPC()
    
        context.request(EDITORCONFIG, file_path=__file__)
    
        sleep(1)
        output: Response | None = context.get_response(EDITORCONFIG)
        print(output)
        context.kill_IPC()
    
    
    if __name__ == "__main__":
        main()

See the file example file `here <https://github.com/salve-org/salve/blob/master/examples/simple_editorconfig_example.py>`_.