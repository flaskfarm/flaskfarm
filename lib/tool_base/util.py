import json
import os
import sys
import traceback

from . import logger


class ToolUtil(object):

    
    
    @classmethod
    def save_dict(cls, data, filepath):
        try:
            import codecs
            import json
            data = json.dumps(data, indent=4, ensure_ascii=False)
            ofp = codecs.open(filepath, 'w', encoding='utf8')
            ofp.write(data)
            ofp.close()
        except Exception as e:
            logger.debug(f"Exception:{str(e)}")
            logger.debug(traceback.format_exc())


    @classmethod
    def dump(cls, data):
        if type(data) in [type({}), type([])]:
            return '\n' + json.dumps(data, indent=4, ensure_ascii=False)
        else:
            return str(data)



    @classmethod
    def sizeof_fmt(cls, num, suffix='B'):
        for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
            if abs(num) < 1024.0:
                return "%3.1f%s%s" % (num, unit, suffix)
            num /= 1024.0
        return "%.2f%s%s" % (num, 'Y', suffix)


    @classmethod
    def timestamp_to_datestr(cls, stamp, format='%Y-%m-%d %H:%M:%S'):
        from datetime import datetime
        tmp = datetime.fromtimestamp(stamp)
        return tmp.strftime(format)
    