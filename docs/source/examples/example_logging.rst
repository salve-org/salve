===============
Example Logging
===============

.. code-block:: python

    from logging import INFO, Logger, basicConfig, getLogger
    from time import sleep
    
    from salve import HIGHLIGHT, IPC, Response
    
    basicConfig(
        level=INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logger: Logger = getLogger("Main")
    
    
    def main():
        context = IPC()
    
        context.update_file(
            "test",
            open(__file__, "r+").read(),
        )
    
        context.request(
            HIGHLIGHT, file="test", language="python", text_range=(1, 30)
        )
    
        sleep(1)
        output: Response | None = context.get_response(HIGHLIGHT)
        if output is None:
            logger.info("Output is None")
    
        logger.info(f"Output: {output}")
    
        context.kill_IPC()
    
    
    if __name__ == "__main__":
        main()

See the file example file `here <https://github.com/Moosems/salve/blob/master/examples/example_logging.py>`_.