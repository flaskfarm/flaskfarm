def d(data):
    if type(data) in [type({}), type([])]:
        import json
        try:
            return '\n' + json.dumps(data, indent=4, ensure_ascii=False)
        except:
            return data
    else:
        return str(data)

from .logger import get_logger

logger = get_logger()

from .base.aes import SupportAES
from .base.discord import SupportDiscord
from .base.file import SupportFile
from .base.os_command import SupportOSCommand
from .base.string import SupportString
from .base.sub_process import SupportSubprocess
from .base.support_sc import SupportSC
from .base.telegram import SupportTelegram
from .base.slack import SupportSlack
from .base.util import (AlchemyEncoder, SingletonClass, SupportUtil,
                        default_headers, pt)
from .base.yaml import SupportYaml
