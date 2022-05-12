import pickle
import os

from .settings.logger import logger
from .settings.base_dir import BASE_DIR


class CookieUtils:

    def __init__(self, driver) -> None:
        self.driver = driver

    def dump_cookies(self, filename: str) -> None:
        if not os.path.exists(f'{BASE_DIR}/src/cookies'):
            os.mkdir(f'{BASE_DIR}/src/cookies')

        pickle.dump(self.driver.get_cookies() , open(f'{BASE_DIR}/src/cookies/{filename}.pkl', 'wb'))
        logger.info(f'Cookies saved to file {filename}.pkl')

    def load_cookies(self, filename: str) -> None:

        if os.path.isfile(f'{BASE_DIR}/src/cookies/{filename}.pkl'):
            cookies = pickle.load(open(f'{BASE_DIR}/src/cookies/{filename}.pkl', 'rb'))

            for cookie in cookies:
                self.driver.add_cookie(cookie)
            logger.info(f'Cookies loaded (filename={filename}.pkl')

        else:
            logger.error(f'File {filename}.pkl does not found')
            raise FileNotFoundError(f'File {filename}.pkl does not found')