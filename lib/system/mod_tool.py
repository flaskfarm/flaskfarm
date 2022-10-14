from support import SupportFile

from .setup import *

name = 'tool'

class ModuleTool(PluginModuleBase):
    def __init__(self, P):
        super(ModuleTool, self).__init__(P, name=name, first_menu='upload')
        self.set_page_list([PageUpload])


class PageUpload(PluginPageBase):
    db_default = {
        'path_upload': os.path.join(F.config['path_data'], 'upload'),
    } 

    def __init__(self, P, parent):
        super(PageUpload, self).__init__(P, parent, name='upload')



class PageCrypt(PluginPageBase):
    def __init__(self, P, parent):
        super(PageCrypt, self).__init__(P, parent, name='crypt')
