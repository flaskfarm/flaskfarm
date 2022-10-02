from functools import wraps

from flask import abort, request


def check_api(original_function):
    @wraps(original_function)
    def wrapper_function(*args, **kwargs):  #1
        from framework import F

        #logger.debug('CHECK API... {} '.format(original_function.__module__))
        #logger.warning(request.url)
        #logger.warning(request.form)
        try:
            if F.SystemModelSetting.get_bool('auth_use_apikey'):
                if request.method == 'POST':
                    apikey = request.form['apikey']
                else:
                    apikey = request.args.get('apikey')
                #apikey = request.args.get('apikey')
                if apikey is None or apikey != F.SystemModelSetting.get('auth_apikey'):
                    F.logger.warning('CHECK API : ABORT no match ({})'.format(apikey))
                    F.logger.warning(request.environ.get('HTTP_X_REAL_IP', request.remote_addr))
                    abort(403)
                    return 
        except Exception as e: 
            F.logger.warning('CHECK API : ABORT exception')
            abort(403)
            return 
        return original_function(*args, **kwargs)  #2
    return wrapper_function

# Suuport를 logger 생성전에 쓰지 않기 위해 중복 선언 
import logging


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
    format = '[{yellow}%(asctime)s{reset}|{color}%(levelname)s{reset}|{green}%(name)s{reset}|%(pathname)s:%(lineno)s] {color}%(message)s{reset}'

    FORMATS = {
        logging.DEBUG: format.format(color=grey, reset=reset, yellow=yellow, green=green),
        logging.INFO: format.format(color=green, reset=reset, yellow=yellow, green=green),
        logging.WARNING: format.format(color=yellow, reset=reset, yellow=yellow, green=green),
        logging.ERROR: format.format(color=red, reset=reset, yellow=yellow, green=green),
        logging.CRITICAL: format.format(color=bold_red, reset=reset, yellow=yellow, green=green)
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


# Suuport를 logger 생성전에 쓰지 않기 위해 중복 선언    
def read_yaml(filepath):
    import yaml
    with open(filepath, encoding='utf8') as file:
    #with open(filepath, 'rb') as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
    return data


class User:
    def __init__(self, user_id, email=None, passwd_hash=None, authenticated=False):
        self.user_id = user_id
        self.email = email
        self.passwd_hash = passwd_hash
        self.authenticated = authenticated

    def __repr__(self):
        r = {
            'user_id': self.user_id,
            'email': self.email,
            'passwd_hash': self.passwd_hash,
            'authenticated': self.authenticated,
        }
        return str(r)

    def can_login(self, passwd_hash):
        from support.base.aes import SupportAES
        tmp = SupportAES.decrypt(self.passwd_hash)
        return passwd_hash == tmp

    def is_active(self):
        return True

    def get_id(self):
        return self.user_id

    def is_authenticated(self):
        return self.authenticated

    def is_anonymous(self):
        return False


