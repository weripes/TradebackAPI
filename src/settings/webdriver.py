import undetected_chromedriver as uc

from .logger import logger


driver = uc.Chrome(headless=True)

logger.debug('Driver initialized')