import json
import os
import traceback

from support import SupportSubprocess, d, logger


class SupportRclone(object):
    __instance_list = []

    __rclone_path = 'rclone'
    __rclone_config_path = 'rclone.conf'


    @classmethod
    def initialize(cls, __rclone_path, __rclone_config_path):
        cls.__rclone_path = __rclone_path
        cls.__rclone_config_path = __rclone_config_path

    @classmethod
    def rclone_cmd(cls):
        return [cls.__rclone_path, '--config', cls.__rclone_config_path]
        
    @classmethod
    def get_version(cls, rclone_path=None):
        try:
            if rclone_path == None:
                rclone_path = cls.__rclone_path
            cmd = [rclone_path, '--version']
            result = SupportSubprocess.execute_command_return(cmd)
            if result != None and result['status'] == 'finish':
                return result['log']
        except Exception as e: 
            logger.error(f'Exception:{str(e)}')
            logger.error(traceback.format_exc())   


    @classmethod
    def config_list(cls, rclone_path=None, rclone_config_path=None, option=None):
        try:
            if rclone_path == None:
                rclone_path = cls.__rclone_path
            if rclone_config_path == None:
                rclone_config_path = cls.__rclone_config_path
            if os.path.exists(rclone_path) == False or os.path.exists(rclone_config_path) == False:
                return
            command = [rclone_path, '--config', rclone_config_path, 'config', 'dump']
            if option is not None:
                command += option
            result = SupportSubprocess.execute_command_return(command, format='json')
            for key, value in result['log'].items():
                if 'token' in value and value['token'].startswith('{'):
                    value['token'] = json.loads(value['token'])
            return result['log']
        except Exception as e: 
            logger.error(f'Exception:{str(e)}')
            logger.error(traceback.format_exc())   


    @classmethod
    def lsjson(cls, remote_path, option=None):
        try:
            command = [cls.__rclone_path, '--config', cls.__rclone_config_path, 'lsjson', remote_path]
            if option is not None:
                command += option
            result = SupportSubprocess.execute_command_return(command, format='json')
            ret = None
            if result != None and result['status'] == 'finish':
                ret = result['log']
                ret = list(sorted(ret, key=lambda k:k['Path']))
            return ret
        except Exception as e: 
            logger.error(f'Exception:{str(e)}')
            logger.error(traceback.format_exc())   
