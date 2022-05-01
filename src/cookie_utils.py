import pickle
import os

from .settings.logger import logger


class CookieUtils:

    def __init__(self, driver) -> None:
        self.driver = driver

    def dump_cookies(self, filename: str) -> None:
        if not os.path.exists('cookies'):
            os.mkdir('cookies')

        pickle.dump(self.driver.get_cookies() , open(f'cookies/{filename}.pkl', 'wb'))
        logger.info(f'Cookies saved to file {filename}.pkl in path /cookies')

    def load_cookies(self, filename: str) -> None:

        if os.path.isfile(f'cookies/{filename}.pkl'):
            cookies = pickle.load(open(f'cookies/{filename}.pkl', 'rb'))

            for cookie in cookies:
                self.driver.add_cookie(cookie)
            logger.info(f'Cookies loaded (filename={filename}.pkl, path /cookies)')

        else:
            logger.error(f'File {filename}.pkl does not found in path /cookies')
            raise FileNotFoundError(f'File {filename}.pkl does not found in path /cookies')