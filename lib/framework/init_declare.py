import os
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
            if F.SystemModelSetting.get_bool('use_apikey'):
                try:
                    d = request.get_json()
                except Exception:
                    d = request.form.to_dict() if request.method == 'POST' else request.args.to_dict()
                apikey = d.get('apikey')
                if apikey is None or apikey != F.SystemModelSetting.get('apikey'):
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

# Support를 logger 생성전에 쓰지 않기 위해 중복 선언 
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
        #from support import SupportAES
        #tmp = SupportAES.decrypt(self.passwd_hash)
        import hashlib
        enc = hashlib.md5()
        enc.update(passwd_hash.encode())
        hash = enc.hexdigest()
        #return True
        return self.passwd_hash == hash

    def is_active(self):
        return True

    def get_id(self):
        return self.user_id

    def is_authenticated(self):
        return self.authenticated

    def is_anonymous(self):
        return False


