import json
import time
import traceback
from functools import wraps

from . import logger


def pt(f):
    @wraps(f)
    def wrapper(*args, **kwds):
        start = time.time()
        #logger.debug(f"FUNC START [{f.__name__}]")
        result = f(*args, **kwds)
        elapsed = time.time() - start
        logger.info(f"FUNC END [{f.__name__}] {elapsed}")
        return result
    return wrapper

default_headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
}


class SupportUtil(object):
    @classmethod
    def sizeof_fmt(cls, num, suffix='Bytes'):
        for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
            if abs(num) < 1024.0:
                return "%3.1f %s%s" % (num, unit, suffix)
            num /= 1024.0
        return "%.1f %s%s" % (num, 'Y', suffix)

    @classmethod
    def is_arm(cls):
        try:
            ret = False
            import platform
            if platform.system() == 'Linux':
                if platform.platform().find('86') == -1 and platform.platform().find('64') == -1:
                    ret = True
                if platform.platform().find('arch') != -1:
                    ret = True
                if platform.platform().find('arm') != -1:
                    ret = True
            return ret
        except Exception as e: 
            logger.error(f"Exception:{str(e)}")
            logger.error(traceback.format_exc())
    

def dummy_func():
    pass
     
class celery(object):
    
    class task(object):
        def __init__(self, *args, **kwargs):
            if len(args) > 0:
                self.f = args[0]
    
        def __call__(self, *args, **kwargs):
            if len(args) > 0 and type(args[0]) == type(dummy_func):
                return args[0]
            self.f(*args, **kwargs)    






class SingletonClass(object):
    __instance = None
    
    @classmethod
    def __getInstance(cls):
        return cls.__instance

    @classmethod
    def instance(cls, *args, **kargs):
        cls.__instance = cls(*args, **kargs)
        cls.instance = cls.__getInstance
        return cls.__instance



class AlchemyEncoder(json.JSONEncoder):

    def default(self, obj):
        from sqlalchemy.ext.declarative import DeclarativeMeta
        if isinstance(obj.__class__, DeclarativeMeta):
            # an SQLAlchemy class
            fields = {}
            for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                data = obj.__getattribute__(field)
                try:
                    json.dumps(data) # this will fail on non-encodable values, like other classes
                    fields[field] = data
                except TypeError:
                    fields[field] = None
            # a json-encodable dict
            return fields

        return json.JSONEncoder.default(self, obj)
