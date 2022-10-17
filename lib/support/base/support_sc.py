import argparse
import os
import platform
import re
import sys
import traceback

from . import logger


class SupportSC:
    LIBRARY_LOADING = False
    try:
        sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'libsc'))
        import sc
        LIBRARY_LOADING = True
    except:
        pass
    

    @classmethod
    def encode(cls, text, mode=0):
        try:
            import sc
            return sc.encode(text, mode)
        except Exception as e:
            logger.error(f'Exception:{str(e)}')
            logger.error(traceback.format_exc())
            return None

        
    @classmethod
    def decode(cls, text):
        try:
            import sc
            return sc.decode(text)
        except:
            return None
    
    @classmethod
    def load_module(cls, module_name, module_code):
        try:
            import sc
            mod = sc.load_module(module_name, module_code)
            sys.modules[mod] = mod
            logger.warning(f"C-LOADING : {module_name}")
            return mod
        except Exception as e:
            logger.error(f'Exception:{str(e)}')
            logger.error(traceback.format_exc())

    @classmethod
    def load_module_P(cls, plugin_ins, filename):
        return cls.load_module_f(plugin_ins.setting['filepath'], filename)

    @classmethod
    def load_module_f(cls, package_filepath, filename):
        dirname = os.path.dirname(package_filepath)
        filepath = os.path.join(dirname, filename + '.pyf')
        if os.path.exists(filepath) and os.path.exists(filepath):
            from support import SupportFile
            code = SupportFile.read_file(filepath)
            return cls.load_module(f"{os.path.basename(dirname)}.{filename}", code)

    @classmethod
    def td(self, mediacode, ts, url):
        try:
            import sc
            ret = sc.td1(mediacode, str(ts), url).strip()
            ret = re.sub('[^ -~]+', '', ret).strip()
            return ret
        except:
            return None
