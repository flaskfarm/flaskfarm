from support import SupportFile

from .setup import *

name = 'tool'

class ModuleTool(PluginModuleBase):
    db_default = {
        'path_upload': os.path.join(F.config['path_data'], 'upload'),
    } 


    def __init__(self, P):
        super(ModuleTool, self).__init__(P, name=name, first_menu='upload')
        

    def process_menu(self, page, req):
        arg = P.ModelSetting.to_dict()
        try:
            return render_template(f'{__package__}_{name}_{page}.html', arg=arg)
        except Exception as e: 
            P.logger.error(f'Exception:{str(e)}')
            P.logger.error(traceback.format_exc())
            return render_template('sample.html', title=f"{__package__}/{name}/{page}")


    def process_command(self, command, arg1, arg2, arg3, req):
        ret = {'ret':'success'}
        if command == 'plugin_install':
            ret = F.PluginManager.plugin_install(arg1)
            
        return jsonify(ret)


    def plugin_load(self):
        try:
            pass
        except Exception as e:
            P.logger.error(f'Exception:{str(e)}')
            P.logger.error(traceback.format_exc())


    