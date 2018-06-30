import logging

logging.basicConfig(filename='test.log',
                    level = logging.DEBUG,
                    format = "%(levelname)s %(asctime)s %(message)s")

logger = logging.getLogger()

logger.info("info message")
logger.debug("debug message")
logger.warning("warning message")
logger.critical("critical message")
