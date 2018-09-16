from time import sleep
import logging
import multiprocessing

from .core import Core

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    c = Core("config.yml")
    server = multiprocessing.Process(target=c.server.serve_forever,
                                     name='server',
                                     args=(('', 5000),))
    server.start()
    logger.info("Initialized")
    try:
        while True:
            sleep(10)
    except:
        pass
