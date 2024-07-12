import logging
import time
import multiprocessing

# Create function to test
def do_something(logger: logging.Logger):
    logger.warn("Function do_something() is deprecated")

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
subprocess_logger = logging.getLogger("mylib")

def main():
    logger.info("Started")

    # Pass the logger to the subprocess
    p = multiprocessing.Process(target=do_something, args=(subprocess_logger,))
    p.start()
    # time.sleep(.5)
    p.join()

    logger.info("Finished")

if __name__ == "__main__":
    main()
