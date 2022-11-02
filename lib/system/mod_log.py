import shutil

from support import SupportFile

from .setup import *

name = 'all_log'

class ModuleLog(PluginModuleBase):
    def __init__(self, P):
        super(ModuleLog, self).__init__(P, name=name, first_menu='list')
        

    def process_menu(self, page, req):
        try:
            arg = {}
            log_files = os.listdir(os.path.join(F.config['path_data'], 'log'))
            log_files.sort()
            log_list = []
            for x in log_files:
                if x.endswith('.log'):
                    log_list.append(x)
            arg['log_list'] = '|'.join(log_list)
            arg['all_list'] = '|'.join(log_files)
            arg['filename'] = 'framework.log'
           
            if 'filename' in request.form:
                arg['filename'] = request.form['filename']
            arg['filename'] = req.args.get('filename', arg['filename'])
            return render_template(f'{__package__}_{name}.html', arg=arg)
        except Exception as e: 
            P.logger.error(f'Exception:{str(e)}')
            P.logger.error(traceback.format_exc())
            return render_template('sample.html', title=f"{__package__}/{name}/{page}")


    def process_command(self, command, arg1, arg2, arg3, req):
        ret = {'ret':'success'}
        if command == 'plugin_install':
            ret = F.PluginManager.plugin_install(arg1)
        elif command == 'get_plugin_list':
            data = []
            """
            for name, entity in F.PluginManager.plugin_list.items():
                if entity['version'] == '3':
                    data.append({'package_name':name})
                else:
                    data.append(entity['P'].plugin_info)
            """
            for name, entity in F.PluginManager.all_package_list.items():
                try:
                    if entity.get('version') == '3':
                        #data.append(entity)
                        data.append({'package_name':name})
                    else:
                        data.append(entity['P'].plugin_info)
                        data[-1]['loading'] = entity.get('loading')
                        data[-1]['status'] = entity.get('status')
                        data[-1]['log'] = entity.get('log')
                except Exception as e:
                    data.append({'package_name':name})
                    P.logger.error(f'Exception:{str(e)}')
                    P.logger.error(traceback.format_exc())
            ret['data'] = data
            #P.logger.debug(data)
        elif command == 'uninstall':
            info = F.PluginManager.all_package_list[arg1]
            if os.path.exists(info['path']):
                try:
                    shutil.rmtree(info['path'])
                    ret['msg'] = '삭제하였습니다.<br>재시작시 적용됩니다.'
                except Exception as e:
                    P.logger.error(f'Exception:{str(e)}')
                    P.logger.error(traceback.format_exc())
                    ret['msg'] = info['path'] + "<br>삭제에 실패하였습니다.<br>" + str(e)
                    ret['ret'] = 'danger'
            else:
                ret['msg'] = info['path'] + "<br>폴더가 없습니다."
                ret['ret'] = 'danger'
        return jsonify(ret)


    def plugin_load(self):
        try:
            pass
        except Exception as e:
            P.logger.error(f'Exception:{str(e)}')
            P.logger.error(traceback.format_exc())


    