import logging


LOG_FORMAT = '[%(levelname)s] %(message)s'
logging.basicConfig(format=LOG_FORMAT)
logger = logging.getLogger()
logger.setLevel(logging.INFO)