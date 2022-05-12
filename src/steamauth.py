from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import time

from .settings.logger import logger


# The function is needed for authorization in any service through Steam
def steam_openid_auth(driver, steam_login: str, steam_password: str):

    openid_url_startswith = 'https://steamcommunity.com/openid/'
    current_url = driver.current_url.startswith(openid_url_startswith)
    if not current_url:
        error_msg = f'Error in "steam_openid_login(). Driver url must starts with "{openid_url_startswith}"'
        logger.error(f'{error_msg}, but driver url is {current_url} ')
        raise AttributeError(error_msg)

    del current_url
    logger.info('Login via steam started')
    steamcommunity_url = driver.current_url
    driver.find_element(by=By.ID, value='steamAccountName').send_keys(steam_login)
    driver.find_element(by=By.ID, value='steamPassword').send_keys(steam_password)
    driver.find_element(by=By.ID, value='imageLogin').click()

    driver_wait_5 = WebDriverWait(driver, 5)
    driver_wait_10 = WebDriverWait(driver, 10)

    # Wait until dispear loading gif
    driver_wait_10.until_not(EC.visibility_of_element_located((By.ID, 'login_btn_wait')))

    time.sleep(2)

    current_url = driver.current_url
    if current_url != steamcommunity_url:
        logger.debug(f'Redirect from {steamcommunity_url} to {current_url} after imageLogin.click')
        return

    # if the redirect did not occur, then is needed confirmation
    try:
        newmodal = driver.find_element(by=By.CLASS_NAME, value='newmodal')

        try:
            newmodal.find_element(by=By.CLASS_NAME, value='loginTwoFactorCodeModal')
            auth_mode = 'TwoFactor'
        except:

            try:
                newmodal.find_element(by=By.CLASS_NAME, value='loginAuthCodeModal')
                auth_mode = 'AuthCode'
            except:
                auth_mode = None

    except:

        try:
            error_display_element = driver.find_element(by=By.ID, value='error_display')
        except:
            error_display_element = None

        incorrect_login_msg = 'The account name or password that you have entered is incorrect.'
        if error_display_element.text == incorrect_login_msg:
            raise AttributeError(incorrect_login_msg)

        else:
            raise ConnectionError("Can't connect with your steam account. Try again later")

    if not auth_mode:
        logger.error('Unknown authorization mode')
        raise ConnectionError('Unknown authorization mode. Working modes - [TwoFactor, Authcode(mail)]')

    newmodal_title = newmodal.find_element(by=By.CLASS_NAME, value='newmodal_header').text
    while True:
        authcode = input(f'[:] {newmodal_title}\n    Input your code and press Enter\n[>] ')
        authcode_input_element = newmodal.find_element(by=By.TAG_NAME, value='input')
        authcode_input_element.clear()
        authcode_input_element.send_keys(authcode)
        time.sleep(1)
        steamcommunity_url = driver.current_url
        authcode_input_element.send_keys(Keys.ENTER)

        if auth_mode == 'TwoFactor':
            loading_gif_element_id = 'login_twofactorauth_buttonset_waiting'
            incorrect_code_element_id = 'login_twofactorauth_message_incorrectcode'
        elif auth_mode == 'AuthCode':
            loading_gif_element_id = 'auth_buttonset_waiting'
            incorrect_code_element_id = 'auth_message_incorrectcode'

        # Wait until disappear loading gif
        driver_wait_10.until_not(
            EC.visibility_of_element_located((By.ID, loading_gif_element_id))
        )
        time.sleep(2)
        current_url = driver.current_url
        if current_url != steamcommunity_url:
            logger.debug(f'Redirected from {steamcommunity_url} to {current_url}')
            return

        # if the redirect did not occur, then needed to click on the continue button
        # or entered code is incorrect or another error occurred
        if auth_mode == 'AuthCode':
            try:
                success_btn = driver.find_element(by=By.ID, value='success_continue_btn')
                success_btn.click()
                current_url = driver.current_url
                if current_url != steamcommunity_url:
                    logger.debug(f'Redirected from {steamcommunity_url} to {current_url}')
                    return

            except:
                pass

        try:
            incorrect_code_element = driver.find_element(by=By.ID, value=incorrect_code_element_id)
            if incorrect_code_element.is_displayed():
                print('[!] Incorrect Steam guard code. Try again')
                logger.error(f'Introduced incorrect code. Code = {authcode}')
                continue

        except:
            logger.error('Login failed')
            raise ConnectionError("Can't connect to your steam account")