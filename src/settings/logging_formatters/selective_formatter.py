import logging


class SelectiveFormatter(logging.Formatter):

    default_format = '[Logger: %(name)s] [%(levelname)s] [Msg: %(msg)s]'
    verbose_format = '[Logger: %(name)s] [%(levelname)s] [%(asctime)s] [Module: %(module)s; Line: %(lineno)d] [Msg: %(msg)s]'

    FORMATS = {
        logging.CRITICAL: verbose_format,
        logging.WARNING: verbose_format,
        logging.ERROR: verbose_format,
        'DEFAULT': default_format,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno, self.FORMATS['DEFAULT'])
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)