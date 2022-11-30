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
    def get_rclone_path(cls):
        return cls.__rclone_path

    @classmethod
    def __get_cmd(cls, config_path=None):
        command = [cls.__rclone_path]
        if config_path == None:
            command += ['--config', cls.__rclone_config_path]
        else:
            command += ['--config', config_path]
        return command


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
            if os.path.exists(rclone_config_path) == False:
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
    def get_config(cls, remote_name, rclone_path=None, rclone_config_path=None, option=None):
        try:
            data = cls.config_list(rclone_path=rclone_path, rclone_config_path=rclone_config_path, option=option)
            return data.get(remote_name, None)
            
        except Exception as e: 
            logger.error(f"Exception:{str(e)}")
            logger.error(traceback.format_exc())


    @classmethod
    def lsjson(cls, remote_path, config_path=None, option=None):
        return cls.__execute_one_param('lsjson', remote_path, config_path=config_path, option=option, format='json')


    @classmethod
    def lsf(cls, remote_path, config_path=None, option=None):
        if option == None:
            option = ['--max-depth=1']
        return cls.__execute_one_param('lsf', remote_path, config_path=config_path, option=option, format='json')


    @classmethod
    def size(cls, remote_path, config_path=None, option=None):
        if option == None:
            option = ['--json']
        return cls.__execute_one_param('size', remote_path, config_path=config_path, option=option, format='json')


    @classmethod
    def mkdir(cls, remote_path, config_path=None, option=None):
        return cls.__execute_one_param('mkdir', remote_path, config_path=config_path, option=option, format='json')

    @classmethod
    def purge(cls, remote_path, config_path=None, option=None):
        return cls.__execute_one_param('purge', remote_path, config_path=config_path, option=option, format='json')


    @classmethod
    def __execute_one_param(cls, command, remote_path, config_path=None, option=None, format=None):
        try:
            command = cls.__get_cmd(config_path) + [command, remote_path]
            if option is not None:
                command += option
            result = SupportSubprocess.execute_command_return(command, format=format)
            ret = None
            if result != None and result['status'] == 'finish':
                ret = result['log']
            return ret
        except Exception as e: 
            logger.error(f'Exception:{str(e)}')
            logger.error(traceback.format_exc())  


    @classmethod
    def copy(cls, src, tar, config_path=None, option=None):
        return cls.__execute_two_param('copy', src, tar, config_path=config_path, option=option)
    
    @classmethod
    def copy_server_side(cls, src, tar, config_path=None, option=None):
        if option == None:
            option = ['--drive-server-side-across-configs=true', '--delete-empty-src-dirs']
        return cls.__execute_two_param('copy', src, tar, config_path=config_path, option=option)

    @classmethod
    def move(cls, src, tar, config_path=None, option=None):
        return cls.__execute_two_param('move', src, tar, config_path=config_path, option=option)

    @classmethod
    def move_server_side(cls, src, tar, config_path=None, option=None):
        if option == None:
            option = ['--drive-server-side-across-configs=true', '--delete-empty-src-dirs']
        return cls.__execute_two_param('move', src, tar, config_path=config_path, option=option)

    @classmethod
    def __execute_two_param(cls, command, src, tar, config_path=None, option=None, format=None):
        try:
            command = cls.__get_cmd(config_path) + [command, src, tar]
            if option is not None:
                command += option
            result = SupportSubprocess.execute_command_return(command, format=format)
            ret = None
            if result != None and result['status'] == 'finish':
                ret = result['log']
            return ret
        except Exception as e: 
            logger.error(f'Exception:{str(e)}')
            logger.error(traceback.format_exc())  



    @classmethod
    def getid(cls, remote_path, config_path=None, option=None):
        try:
            command = cls.__get_cmd(config_path) + ['backend', 'getid', remote_path]
            if option is not None:
                command += option
            result = SupportSubprocess.execute_command_return(command)
            ret = None
            if result != None and result['status'] == 'finish':
                ret = result['log']
            if ret is not None and (len(ret.split(' ')) > 1 or ret == ''):
                ret = None
            return ret
        except Exception as e: 
            logger.error(f"Exception:{str(e)}")
            logger.error(traceback.format_exc())


    @classmethod
    def chpar(cls, src, tar, config_path=None, option=None):
        try:
            command = cls.__get_cmd(config_path) + ['backend', 'chpar', src, tar, '-o', 'depth=1', '-o', 'delete-empty-src-dir', '--drive-use-trash=false']
            if option is not None:
                command += option
            result = SupportSubprocess.execute_command_return(command)
            ret = None
            if result != None and result['status'] == 'finish':
                ret = result['log']
            return True
        except Exception as e: 
            logger.error(f"Exception:{str(e)}")
            logger.error(traceback.format_exc())
        return False