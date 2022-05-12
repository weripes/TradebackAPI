import logging
import logging.config
import os

from .base_dir import BASE_DIR
from .logging_formatters.selective_formatter import SelectiveFormatter


if not os.path.exists(f'{BASE_DIR}/src/logging'):
    os.mkdir(f'{BASE_DIR}/src/logging')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '[{name}({levelname})] | {message}',
            'style': '{',
        },
        'SelectiveFormatter': {
            '()': SelectiveFormatter
        }
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'DEBUG',
            'formatter': 'SelectiveFormatter',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': f'{BASE_DIR}/src/logging/logs.log',
            'mode': 'a',
            'maxBytes': 1 * 1000 * 1000,
            'backupCount': 5,
        },
    },
    'loggers': {
        'TradeBack': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        }
    }
}

logging.config.dictConfig(LOGGING)
logger = logging.getLogger('TradeBack')