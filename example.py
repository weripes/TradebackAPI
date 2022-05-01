from src.settings.webdriver import driver
from src.parameters import ParametersModel
from src.tradebackapi import TradeBackAPI

import json
import os

if __name__ == '__main__':

    test1_parameters = ParametersModel(
        app='all',
        first_service='steamcommunity.com',
        second_service='dmarket.com',
        first_service_categories=['orders'],
        second_service_categories=['normal'],
        second_to_first_service_profit_from=45,
        second_service_price_from=0.5,
        sort_by='second_to_first_service_descending_profit',
    )

    test2_parameters = ParametersModel(
        app='csgo',
        first_service='steamcommunity.com',
        second_service='bitskins.com',
        first_service_categories=['normal', 'orders'],
        second_service_categories=['normal'],
        first_to_second_service_profit_from=-20,
        first_service_price_from=0.5,
        sort_by='first_to_second_service_descending_profit',
        sales_per_week= {
            'SteamCommunity.com': 150,
            'BitSkins.com': 10
        }
    )

    test3_parameters = ParametersModel(
        app='csgo',
        first_service='steamcommunity.com',
        second_service='cs.money',
        first_service_categories=['normal'],
        second_service_categories=['hold', 'deposit'],
        first_service_price_from=1,
        second_service_hold_time=5,
        sort_by='first_service_descending_price',
        sales_per_week={
            'CS & Dota Money': 25
        }
    )

    TradeBack = TradeBackAPI(driver=driver)

    steam_login=os.getenv('STEAM_LOGIN'),
    steam_password=os.getenv('STEAM_PASSWORD')

    cookie_filename = steam_login

    try:
        TradeBack.login_via_cookies(filename=cookie_filename)
    except:
        # if login via cookies didn't work (ex. file doesn't exists)
        TradeBack.login_via_steam(steam_login=steam_login, steam_password=steam_password)
    finally:
        # Save or update cookies
        TradeBack.save_cookies(filename=cookie_filename)

    test1_items_data = TradeBack.collect_skins(Parameters=test1_parameters)
    test2_items_data = TradeBack.collect_skins(Parameters=test2_parameters)
    test3_items_data = TradeBack.collect_skins(Parameters=test3_parameters)

    with open('test1_items_data.json', 'w') as file:
        file.write(str(json.dumps(test1_items_data)))
        file.close()

    with open('test2_items_data.json', 'w') as file:
        file.write(str(json.dumps(test2_items_data)))
        file.close()

    with open('test3_items_data.json', 'w') as file:
        file.write(str(json.dumps(test3_items_data)))
        file.close()

    TradeBack.logout()