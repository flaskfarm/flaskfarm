def d(data):
    if type(data) in [type({}), type([])]:
        import json
        return '\n' + json.dumps(data, indent=4, ensure_ascii=False)
    else:
        return str(data)

from .logger import get_logger
logger = get_logger()

def set_logger(l):
    global logger
    logger = l

# 일반 cli 사용 겸용이다.
# set_logger 로 인한 진입이 아니고 import가 되면 기본 경로로 로그파일을
# 생성하기 때문에, set_logger 전에 import가 되지 않도록 주의.
