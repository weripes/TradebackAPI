from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import time

from .settings.logger import logger
from .cookie_utils import CookieUtils
from .parameters import ParametersModel, ParametersUtils
from .steamauth import steam_openid_auth


class TradeBackAPI:

    def __init__(self, driver) -> None:
        self.driver = driver
        self.Cookie_Utils = CookieUtils(driver=self.driver)
        self.base_url = 'https://tradeback.io/en/'

        logger.debug('SkinsTable driver initialized')
    
    # If there is a logout button, then are logged in.
    def is_logged_in(self) -> bool:

        try:
            """
            if the logout button appear within 5 seconds, then
            can log out of the account -> are logged in.
            5 seconds in case the site did not load, if the
            function is called immediately after the get request
            """
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'logout-btn'))
            )
            logger.info('User is logged in')
            return True

        except:
            logger.info('User is not logged in')
            return False

    def login_via_steam(self, steam_login, steam_password):

        self.driver.get(f'https://tradeback.io/auth/steam')
        time.sleep(2)
        steam_openid_auth(
            driver=self.driver,
            steam_login=steam_login, steam_password=steam_password
        )
        time.sleep(2)
        if not self.is_logged_in():
            logger.error('Unsuccessfully login via steam')
            raise ConnectionError('Unsuccessfully login via steam')
        logger.info('Successfully logged in via steam')

    def login_via_cookies(self, filename: str):

        self.driver.get(self.base_url)
        self.Cookie_Utils.load_cookies(filename=filename)
        self.driver.get(self.base_url)

        if not self.is_logged_in():
            logger.info('Unsuccessfully logged in via cookies')
            raise ConnectionError(f'Failed to load cookies (filename={filename})')
        logger.info('Successfully logged in via cookies')

    def save_cookies(self, filename: str):
        self.driver.get(self.base_url)
        self.Cookie_Utils.dump_cookies(filename=filename)
        self.driver.get(self.base_url)

    def logout(self):
        try:
            logout_btn = self.driver.find_element(by=By.CLASS_NAME, value='logout-btn')
            logout_btn.click()
            logger.info('Successfully logout')
        except:
            raise ConnectionError("You aren't logged in")

    def collect_skins(self, Parameters: ParametersModel):

        logger.info('Parameters setting...')
        formatted_parameters = ParametersUtils().format_parameters_to_url_path(Parameters=Parameters)
        url = f'{self.base_url}comparison#{formatted_parameters}'
        self.driver.get(url)
        time.sleep(4)
        self.driver.refresh()
        # Refresh is needed due to the specifics of the site

        # the overall table load depends on the autoupdate_status, if status is not received
        # after 10 attemps - try to reload the page, after 3 failed attempts throw an exception
        break_flag = False
        for attemp in range(3):
            logger.debug(f'Attemp {attemp+1} to get autoupdate status')
            for _ in range(10):
                autoupdate_status = self.driver.find_element(
                    by=By.ID, value='auto-update-status-title'
                )
                if autoupdate_status.text in ('(on)', '(off)'):
                    logger.debug('Autoupdate status received')
                    break_flag = True
                    break

                time.sleep(1)

            if break_flag:
                break

            self.driver.refresh()

        if not autoupdate_status.text:
            raise ConnectionError('Failed to load site page. Try again later')

        logger.debug(f'autoupdate_status = {autoupdate_status.text}')
        # Disable autoupdate. If not disabled, then the table will be constantly
        # updated and will not allow to collect data
        if autoupdate_status.text == '(on)':
            autoupdate_status.click()
            autoupdate_checkbox = self.driver.find_element(by=By.ID, value='auto-update-live')
            time.sleep(1)
            autoupdate_checkbox.find_element(by=By.XPATH, value="..").click()
            time.sleep(1)
            autoupdate_status.click()
            logger.debug('Autoupdate disabled')

        time.sleep(2)
        # If parameters are not set, then the fields
        # will be cleared, if there are, new values ​​will be inserted
        more_filters_button = self.driver.find_element(by=By.ID, value='more-filters')
        more_filters_button.click()
        time.sleep(2)
        market_sales_blocks = self.driver.find_elements(by=By.CLASS_NAME, value='comparison-sales-block')

        for market_block in market_sales_blocks:
            market_name = market_block.find_element(by=By.TAG_NAME, value='p').text
            try:
                sales_count = Parameters.sales_per_week[market_name]
            except:
                sales_count = None
            finally:
                time.sleep(1)
                input_sales_element = market_block.find_element(by=By.TAG_NAME, value='input')
                input_sales_element.clear()
                if sales_count:
                    input_sales_element.send_keys(sales_count)

        self.driver.find_element(by=By.CLASS_NAME, value='iziModal-button-close').click()

        if Parameters.sort_by:
            if Parameters.sort_by.endswith('price'):
                sort_column = 'price'
            else:
                sort_column = 'profit'

            sort_buttons = self.driver.find_elements(by=By.CLASS_NAME, value=f'column-{sort_column}')

            if Parameters.sort_by.startswith('first'):
                sort_button = sort_buttons[0].find_element(by=By.TAG_NAME, value='i')
            else:
                sort_button = sort_buttons[1].find_element(by=By.TAG_NAME, value='i')

            if 'ascending' in Parameters.sort_by:
                sort_direction = 'asc'
            else:
                sort_direction = 'desc'
            
            # Press the sort button until get the desired value. After
            # clicking the class changes either to ascending or descending
            for _ in range(2):
                sort_button.click()
                sort_button_class = sort_button.get_attribute('class')
                logger.debug(f'sort button class = "{sort_button_class}"')
                if sort_button_class.endswith(sort_direction):
                    break
        
        # Inserting a parameter into the search string
        if Parameters.search_item_string:
            search_item_input = self.driver.find_element(by=By.ID, value='search-item')
            search_item_input.clear()
            search_item_input.send_keys(Parameters.search_item_string)

        # then needed to scroll the page to the bottom to load the entire table
        SCROLL_PAUSE_TIME = 2

        # Get scroll height
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        while True:
            # Scroll down to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load page
            time.sleep(SCROLL_PAUSE_TIME)

            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # Collecting and saving data to a dictionary
        table_body_element = self.driver.find_element(by=By.ID, value='table-body')
        table_rows_elements = table_body_element.find_elements(by=By.TAG_NAME, value='tr')

        items_data = []

        for table_row in table_rows_elements:
            item_name = table_row.find_element(by=By.CLASS_NAME, value='copy-name').text
            services_prices = table_row.find_elements(by=By.CLASS_NAME, value='price')
            first_service_price = services_prices[0].text
            second_service_price = services_prices[1].text
            profit_values = table_row.find_elements(by=By.CLASS_NAME, value='field-profit')
            first_to_second_service_profit = profit_values[1].text
            second_to_first_service_profit = profit_values[0].text

            items_data.append(
                {
                    'item_name': item_name,
                    'first_service_price': first_service_price,
                    'second_service_price': second_service_price,
                    'first_to_second_service_profit': first_to_second_service_profit,
                    'second_to_first_service_profit': second_to_first_service_profit
                }
            )

        logger.info('Items data collected')
        return items_data