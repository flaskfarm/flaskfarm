def d(data):
    if type(data) in [type({}), type([])]:
        import json
        try:
            return '\n' + json.dumps(data, indent=4, ensure_ascii=False)
        except:
            return data
    else:
        return str(data)

def load():
    from .base.aes import SupportAES
    from .base.discord import SupportDiscord
    from .base.file import SupportFile
    from .base.process import SupportProcess
    from .base.string import SupportString
    from .base.subprocess import SupportSubprocess
    from .base.telegram import SupportTelegram
    from .base.util import (AlchemyEncoder, SingletonClass, SupportUtil,
                            default_headers, pt)
    from .base.yaml import SupportYaml

import os

logger = None

if os.environ.get('FF') == 'true':
    def set_logger(l):
        global logger
        logger = l
    
else:
    from .logger import get_logger
    logger = get_logger()


from .base.aes import SupportAES
from .base.discord import SupportDiscord
from .base.file import SupportFile
from .base.process import SupportProcess
from .base.string import SupportString
from .base.subprocess import SupportSubprocess
from .base.telegram import SupportTelegram
from .base.util import (AlchemyEncoder, SingletonClass, SupportUtil,
                        default_headers, pt)
from .base.yaml import SupportYaml

# 일반 cli 사용 겸용이다.
# set_logger 로 인한 진입이 아니고 import가 되면 기본 경로로 로그파일을
# 생성하기 때문에, set_logger 전에 import가 되지 않도록 주의.
