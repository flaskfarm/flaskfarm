import os
import platform

from . import logger


class SupportOSCommand(object):

    @classmethod
    def get_size(cls, path):
        from support import SupportFile, SupportSubprocess, SupportUtil
        if platform.system() == 'Windows':
            #https://docs.microsoft.com/en-us/sysinternals/downloads/du
            """
            bin = r'C:\SJVA3\data\bin\du64.exe'
            command = [bin, '-c', '-nobanner', f'"{path}"']
            data = ToolSubprocess.execute_command_return(command, force_log=True)
            logger.warning(data)
            ret = {}
            tmp = data.split('\t')
            ret['target'] = tmp[1].strip()
            ret['size'] = int(tmp[0].strip())
            ret['sizeh'] = ToolUtil.sizeof_fmt(ret['size'])
            """
            ret = {}
            ret['target'] = path
            if os.path.exists(path):
                if os.path.isdir(path):
                    ret['size'] = SupportFile.size(start_path=path)
                else:
                    ret['size'] = os.stat(path).st_size
            ret['sizeh'] = SupportUtil.sizeof_fmt(ret['size'])
            return ret

        else:
            command = ['du', '-bs', path]
            data = SupportSubprocess.execute_command_return(command)
            ret = {}
            tmp = data['log'].split('\t')
            ret['target'] = tmp[1].strip()
            ret['size'] = int(tmp[0].strip())
            ret['sizeh'] = SupportUtil.sizeof_fmt(ret['size'])
        return ret
            