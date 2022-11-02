import traceback

from . import logger


class ToolUtil(object):

    @classmethod
    def make_apikey_url(cls, url):
        from framework import F
        if not url.startswith('http'):
            url = F.SystemModelSetting.get('ddns') + url
        if F.SystemModelSetting.get_bool('use_apikey'):
            if url.find('?') == -1:
                url += '?'
            else:
                url += '&'
            url += f"apikey={F.SystemModelSetting.get('apikey')}"
        return url
    
    @classmethod
    def make_path(cls, data):
        from framework import F
        return data.replace('{PATH_DATA}', F.config['path_data'])
    

    @classmethod
    def run_system_command_by_id(cls, command_id):
        try:
            from system.setup import P as PP
            page_ins = PP.logic.get_module('tool').get_page('command')
            thread = page_ins.execute_thread_start(command_id)
            return thread
        except Exception as e: 
            logger.error(f'Exception:{str(e)}')
            logger.error(traceback.format_exc())  

