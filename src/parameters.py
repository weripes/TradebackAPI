from pydantic import BaseModel

from dataclasses import dataclass
from typing import Literal
import json


@dataclass
class ParametersDataTypes:
    app_values = Literal['all', 'vgo', 'csgo', 'dota2', 'h1z1', 'rust', 'pubg', 'tf2', 'virl']
    service_values = Literal[
        'steamcommunity.com', 'bitskins.com',      'tm_market',          'dmarket.com',
        'skinsdealer.com',    'skinkeen.ru',       'cs.money',           'dota.money',
        'loot.farm',          'tradeit.gg',        'swap.gg',            'cs.deals',
        'cs.trade',           'keys-store.com',    'tradeskinsfast.com', 'tradedota2.com',
        'bets4.pro',          'cs.deals_market',   'mannco.trade',       'csgoexo.com',
        'csgofast.com',       'dota2bestyolo.com', 'godota2.com'
    ]
    category_values = list[Literal['normal', 'hold', 'deposit', 'orders']]
    sales_per_week_values = dict[
        Literal[
            'OPSkins.com',
            'SteamCommunity.com',
            'CS & Dota Money',
            'BitSkins.com',
            'TM Market'
        ], int]
    sort_by_values = Literal[
            'first_service_ascending_price',
            'first_service_descending_price',
            'second_service_ascending_price',
            'second_service_descending_price',
            'first_to_second_service_descending_profit',
            'second_to_first_service_descending_profit'
        ]


class ParametersModel(BaseModel):

    app: ParametersDataTypes.app_values
    first_service: ParametersDataTypes.service_values
    second_service: ParametersDataTypes.service_values
    first_service_categories: ParametersDataTypes.category_values
    second_service_categories: ParametersDataTypes.category_values
    first_service_updated: int = None
    second_service_updated: int = None
    first_service_hold_time: int = None
    second_service_hold_time: int = None
    first_service_price_from: float = None
    first_service_price_to: float = None
    second_service_price_from: float = None
    second_service_price_to: float = None
    first_service_count_from: int = None
    first_service_count_to: int = None
    second_service_count_from: int = None
    second_service_count_to: int = None
    first_to_second_service_profit_from: float = None
    first_to_second_service_profit_to: float = None
    second_to_first_service_profit_from: float = None
    second_to_first_service_profit_to: float = None
    sort_by: ParametersDataTypes.sort_by_values = None
    search_item_string: str = None
    sales_per_week: ParametersDataTypes.sales_per_week_values = None


class ParametersUtils:

    def get_app_id(self, app: ParametersDataTypes.app_values) -> int:
        app_ids = {'all': 'all',
            'vgo': 1, 'csgo': 2, 'dota2': 3, 'h1z1': 4,
            'rust': 5, 'pubg': 6, 'tf2': 7, 'virl': 8
        }
        if app not in app_ids:
            raise AttributeError(f'Error in get_app_id(), argument "app" value must be in {list(app_ids.keys())}')
        return app_ids[app]

    def format_parameters_to_url_path(self, Parameters: ParametersModel) -> str:
        string_parameters = {
            "app": self.get_app_id(app=Parameters.app),
            "services":[Parameters.first_service, Parameters.second_service],
            "updated":[Parameters.first_service_updated, Parameters.second_service_updated],
            "categories":[Parameters.first_service_categories, Parameters.second_service_categories],
            "hold_time_range":[Parameters.first_service_hold_time, Parameters.second_service_hold_time],
            "price":[
                [Parameters.first_service_price_from, Parameters.first_service_price_to],
                [Parameters.second_service_price_from, Parameters.second_service_price_to]
            ],
            "count":[
                [Parameters.first_service_count_from, Parameters.first_service_count_to],
                [Parameters.second_service_count_from, Parameters.second_service_count_to]
            ],
            "profit":[
                [Parameters.first_to_second_service_profit_from, Parameters.first_to_second_service_profit_to],
                [Parameters.second_to_first_service_profit_from, Parameters.second_to_first_service_profit_to]
            ]
        }
        return json.dumps(string_parameters).replace(' ', '')
