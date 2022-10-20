import logging
import logging.handlers
import os
import sys
from datetime import datetime

from pytz import timezone, utc

"""
ConsoleColor.Black => "\x1B[30m",
            ConsoleColor.DarkRed => "\x1B[31m",
            ConsoleColor.DarkGreen => "\x1B[32m",
            ConsoleColor.DarkYellow => "\x1B[33m",
            ConsoleColor.DarkBlue => "\x1B[34m",
            ConsoleColor.DarkMagenta => "\x1B[35m",
            ConsoleColor.DarkCyan => "\x1B[36m",
            ConsoleColor.Gray => "\x1B[37m",
            ConsoleColor.Red => "\x1B[1m\x1B[31m",
            ConsoleColor.Green => "\x1B[1m\x1B[32m",
            ConsoleColor.Yellow => "\x1B[1m\x1B[33m",
            ConsoleColor.Blue => "\x1B[1m\x1B[34m",
            ConsoleColor.Magenta => "\x1B[1m\x1B[35m",
            ConsoleColor.Cyan => "\x1B[1m\x1B[36m",
            ConsoleColor.White => "\x1B[1m\x1B[37m",
"""

class CustomFormatter(logging.Formatter):
    """Logging Formatter to add colors and count warning / errors"""

    grey = "\x1b[38;21m"
    yellow = "\x1b[33;21m"
    red = "\x1b[31;21m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    green = "\x1B[32m"
    # pathname filename
    #format = "[%(asctime)s|%(name)s|%(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
    
    __format = '[{yellow}%(asctime)s{reset}|{color}%(levelname)s{reset}|{green}%(name)s{reset} %(pathname)s:%(lineno)s] {color}%(message)s{reset}' if os.environ.get('LOGGER_PATHNAME', "False") == "True" else '[{yellow}%(asctime)s{reset}|{color}%(levelname)s{reset}|{green}%(name)s{reset} %(filename)s:%(lineno)s] {color}%(message)s{reset}'

    FORMATS = {
        logging.DEBUG: __format.format(color=grey, reset=reset, yellow=yellow, green=green),
        logging.INFO: __format.format(color=green, reset=reset, yellow=yellow, green=green),
        logging.WARNING: __format.format(color=yellow, reset=reset, yellow=yellow, green=green),
        logging.ERROR: __format.format(color=red, reset=reset, yellow=yellow, green=green),
        logging.CRITICAL: __format.format(color=bold_red, reset=reset, yellow=yellow, green=green)
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def get_logger(name=None, log_path=None):
    if os.environ.get('FF') == 'true':
        name = 'framework'
    if name == None:
        name = sys.argv[0].rsplit('.', 1)[0]
    logger = logging.getLogger(name)
    if not logger.handlers:
        level = logging.DEBUG
        logger.setLevel(level)
        formatter = logging.Formatter(u'[%(asctime)s|%(levelname)s|%(filename)s:%(lineno)s] %(message)s')
        def customTime(*args):
            utc_dt = utc.localize(datetime.utcnow())
            my_tz = timezone("Asia/Seoul")
            converted = utc_dt.astimezone(my_tz)
            return converted.timetuple()

        formatter.converter = customTime
        file_max_bytes = 1 * 1024 * 1024 
        if log_path == None:
            log_path = os.path.join(os.getcwd(), 'tmp')
        os.makedirs(log_path, exist_ok=True)
        fileHandler = logging.handlers.RotatingFileHandler(filename=os.path.join(log_path, f'{name}.log'), maxBytes=file_max_bytes, backupCount=5, encoding='utf8', delay=True)
        streamHandler = logging.StreamHandler() 

        fileHandler.setFormatter(formatter)
        streamHandler.setFormatter(CustomFormatter()) 
        
        logger.addHandler(fileHandler)
        logger.addHandler(streamHandler)
    return logger

