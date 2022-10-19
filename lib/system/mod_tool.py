from support import SupportFile

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

