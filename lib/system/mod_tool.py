from support import SupportSubprocess
from tool import ToolModalCommand

from .page_command import PageCommand
from .setup import *

name = 'tool'

class ModuleTool(PluginModuleBase):
    def __init__(self, P):
        super(ModuleTool, self).__init__(P, name=name, first_menu='command')
        
        self.set_page_list([PageUpload, PageCrypt, PagePython, PageCommand])



class PageUpload(PluginPageBase):
    db_default = {
        'path_upload': os.path.join(F.config['path_data'], 'upload'),
    } 

    def __init__(self, P, parent):
        super(PageUpload, self).__init__(P, parent, name='upload')



class PageCrypt(PluginPageBase):
    def __init__(self, P, parent):
        super(PageCrypt, self).__init__(P, parent, name='crypt')

        self.db_default = {
            f'{self.parent.name}_{self.name}_use_user_key': 'False',
            f'{self.parent.name}_{self.name}_user_key': '',
            f'{self.parent.name}_{self.name}_user_key': '',
        } 

class PagePython(PluginPageBase):
    def __init__(self, P, parent):
        super(PagePython, self).__init__(P, parent, name='python')
        self.db_default = {
            f'{self.parent.name}_{self.name}_name': '',
        } 

    def process_command(self, command, arg1, arg2, arg3, req):
        ret = {'ret':'success'}
        if command == 'get_freeze':
            command = ['pip', 'freeze']
            result = SupportSubprocess.execute_command_return(command)
            if result['status'] == 'finish':
                ret['data'] = []
                for tmp in result['log'].split('\n'):
                    if '==' in tmp:
                        ret['data'].append(tmp.split('=='))
            else:
                ret['ret'] = 'danger'
                ret['msg'] = "실패"
        elif command == 'upgrade':
            P.ModelSetting.set(f'{self.parent.name}_{self.name}_name', arg1)
            cmd = ['pip', 'install', '--upgrade', arg1]
            ToolModalCommand.start("pip 설치", [cmd])
        elif command == 'remove':
            cmd = ['pip', 'uninstall', '-y', arg1]
            ToolModalCommand.start("pip 삭제", [cmd])
        return jsonify(ret)
