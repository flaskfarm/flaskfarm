import os
import platform
import shutil
import sys
import threading
import traceback
import zipfile

import requests
from framework import F
from support import SupportFile, SupportSubprocess, SupportYaml


class PluginManager:
    plugin_list = {}
    plugin_menus = {}
    setting_menus = []
    all_package_list = {}


    @classmethod 
    def get_plugin_name_list(cls):
        plugins = []
        #2019-07-17 
        try:
            plugin_path = os.path.join(F.config['path_data'], 'plugins')
            if os.path.exists(plugin_path) == True and os.path.isdir(plugin_path) == True:
                sys.path.insert(1, plugin_path)
                tmps = os.listdir(plugin_path)
                add_plugin_list = []
                for t in tmps:
                    if not t.startswith('_') and os.path.isdir(os.path.join(plugin_path, t)) and t != 'false':
                        add_plugin_list.append(t)
                        cls.all_package_list[t] = {'pos':'normal', 'path':os.path.join(plugin_path, t), 'loading':(F.config.get('plugin_loading_only_devpath', None) != True)}

                plugins = plugins + add_plugin_list
        except Exception as e:
            F.logger.error(f"Exception:{str(e)}")
            F.logger.error(traceback.format_exc())
        
        if F.config.get('plugin_loading_only_devpath', None) == True:
            plugins = []

        # 2018-09-04
        try:
            #plugin_path = F.SystemModelSetting.get('plugin_dev_path')
            plugin_path = F.config['path_dev']
            plugin_path_list = []
            if type(plugin_path) == type(''):
                plugin_path_list = [plugin_path]
            elif type(plugin_path) == type([]):
                plugin_path_list = plugin_path

            for __ in plugin_path_list:
                if __ != None and __ != '':
                    if os.path.exists(__):
                        sys.path.insert(0, __)
                        tmps = os.listdir(__)
                        add_plugin_list = []
                        for t in tmps:
                            if not t.startswith('_')  and os.path.isdir(os.path.join(__, t)) and t != 'false':
                                add_plugin_list.append(t)
                                cls.all_package_list[t] = {'pos':'dev', 'path':os.path.join(__, t), 'loading':True}
                        plugins = plugins + add_plugin_list
        except Exception as e:
            F.logger.error(f"Exception:{str(e)}")
            F.logger.error(traceback.format_exc())

        # plugin_loading_list
        try:
            plugin_loading_list = F.config.get('plugin_loading_list', None)
            if plugin_loading_list != None and (type(plugin_loading_list) == type([]) and len(plugin_loading_list)) > 0:
                new_plugins = []
                for _ in plugins:
                    if _ in plugin_loading_list:
                        new_plugins.append(_)
                    else:
                        cls.all_package_list[_]['loading'] = False
                        cls.all_package_list[_]['status'] = 'not_include_loading_list'
                plugins = new_plugins
        except Exception as e:
            F.logger.error(f"Exception:{str(e)}")
            F.logger.error(traceback.format_exc())

        # plugin_except_list
        try:
            plugin_except_list = F.config.get('plugin_except_list', None)
            if plugin_except_list != None and (type(plugin_except_list) == type([]) and len(plugin_except_list)) > 0:
                new_plugins = []
                for _ in plugins:
                    if _ not in plugin_except_list:
                        new_plugins.append(_)
                    else:
                        cls.all_package_list[_]['loading'] = False
                        cls.all_package_list[_]['status'] = 'include_except_list'
                plugins = new_plugins
        except Exception as e:
            F.logger.error(f"Exception:{str(e)}")
            F.logger.error(traceback.format_exc())
        return plugins



    # menu, blueprint, plugin_info, plugin_load, plugin_unload
    @classmethod
    def plugin_init(cls):
        try:
            plugins = cls.get_plugin_name_list()
            plugins = sorted(plugins)

            F.logger.debug(plugins)
            for plugin_name in plugins:
                F.logger.debug(f'[+] PLUGIN LOADING Start.. [{plugin_name}]') 
                entity = cls.all_package_list[plugin_name]
                try:
                    try:
                        mod = __import__(f'{plugin_name}.setup', fromlist=['setup'])
                    except Exception as e:
                        F.logger.error(f'Exception:{str(e)}')
                        F.logger.error(traceback.format_exc())
                        F.logger.warning(f'[!] NOT normal plugin : [{plugin_name}]')
                        continue

                    try:
                        entity['setup_mod'] = mod
                        entity['P'] = getattr(mod, 'P')
                        mod_blue_print = getattr(entity['P'], 'blueprint')
                        if mod_blue_print: 
                            F.app.register_blueprint(mod_blue_print)
                    except Exception as exception:
                        F.logger.warning(f'[!] BLUEPRINT not exist : [{plugin_name}]') 
                    cls.plugin_list[plugin_name] = entity
                except Exception as e:
                    F.logger.error(f"Exception:{str(e)}")
                    F.logger.error(traceback.format_exc())
                    F.logger.debug('no blueprint')
                    cls.all_package_list[plugin_name]['loading'] = False
                    cls.all_package_list[plugin_name]['status'] = 'import fail'
                    cls.all_package_list[plugin_name]['log'] = traceback.format_exc()
            
            
            if not F.config['run_celery']:
                try:
                    with F.app.app_context(): 
                        F.db.create_all()
                except Exception as e:
                    F.logger.error(f"Exception:{str(e)}")
                    F.logger.error(traceback.format_exc())
                    F.logger.debug('db.create_all error')

            for key, entity in cls.plugin_list.items():
                try:
                    mod_plugin_load = getattr(entity['P'], 'plugin_load_celery')
                    if mod_plugin_load:
                        def func(mod_plugin_load, key):
                            try:
                                #F.logger.debug(f'[!] plugin_load_celery threading start : [{key}]') 
                                mod_plugin_load()
                                #F.logger.debug(f'[!] plugin_load_celery threading end : [{key}]') 
                            except Exception as e:
                                F.logger.error(f"Exception:{str(e)}")
                                F.logger.error(traceback.format_exc())
                        t = threading.Thread(target=func, args=(mod_plugin_load, key))
                        t.setDaemon(True)
                        t.start()
                except Exception as e:
                    F.logger.error(f"Exception:{str(e)}")
                    F.logger.error(traceback.format_exc())

            if not F.config['run_flask']:
                return
            
            for key, entity in cls.plugin_list.items():
                try:
                    mod_plugin_load = getattr(entity['P'], 'plugin_load')
                    if mod_plugin_load:
                        def func(mod_plugin_load, key):
                            try:
                                F.logger.info(f'[!] plugin_load threading start : [{key}]') 
                                mod_plugin_load()
                                F.logger.debug(f'[!] plugin_load threading end : [{key}]') 
                            except Exception as e:
                                F.logger.error('### plugin_load exception : %s', key)
                                F.logger.error(f"Exception:{str(e)}")
                                F.logger.error(traceback.format_exc())
                                cls.all_package_list[key]['loading'] = False
                                cls.all_package_list[key]['status'] = 'plugin_load error'
                                cls.all_package_list[key]['log'] = traceback.format_exc()

                                if key in cls.plugin_menus:
                                    del cls.plugin_menus[key]
                                    F.logger.info(f"플러그인 로딩 실패로 메뉴 삭제1 : {key}")
                                    from framework.init_menu import MenuManager
                                    MenuManager.init_menu()
                                    F.logger.info(f"플러그인 로딩 실패로 메뉴 삭제2 : {key}")

                        t = threading.Thread(target=func, args=(mod_plugin_load, key))
                        t.setDaemon(True)
                        t.start()

                except Exception as e:
                    F.logger.debug(f'[!] PLUGIN_LOAD function not exist : [{key}]') 

                try:
                    mod_menu = getattr(entity['P'], 'menu')
                    if mod_menu and cls.all_package_list[key]['loading'] != False:
                        cls.plugin_menus[key]=  {'menu':mod_menu, 'match':False}
                    setting_menu = getattr(entity['P'], 'setting_menu')
                    setting_menu['plugin'] = entity['P'].package_name
                    if setting_menu != None and cls.all_package_list[key]['loading'] != False:
                        F.logger.info(f"확장 설정 : {key}")
                        cls.setting_menus.append(setting_menu)
                except Exception as exception:
                    F.logger.debug('no menu')
            F.logger.debug('### plugin_load threading all start.. : %s ', len(cls.plugin_list))
            # 모든 모듈을 로드한 이후에 app 등록, table 생성, start

        except Exception as e:
            F.logger.error(f"Exception:{str(e)}")
            F.logger.error(traceback.format_exc())



    @classmethod
    def plugin_unload(cls):
        for key, entity in cls.plugin_list.items():
            try:
                mod_plugin_unload = getattr(entity['P'], 'plugin_unload')
                if mod_plugin_unload:
                    mod_plugin_unload()
            except Exception as e:
                F.logger.error('module:%s', key)
                F.logger.error(f'Exception:{str(e)}')
                F.logger.error(traceback.format_exc())
        try:
            from system.setup import P
            P.plugin_unload()
        except Exception as e:
            F.logger.error(f'Exception:{str(e)}')
            F.logger.error(traceback.format_exc())

    @classmethod
    def plugin_install(cls, plugin_git, zip_url=None, zip_filename=None):
        plugin_git = plugin_git.strip()
        is_git = True if plugin_git != None and plugin_git != '' else False
        ret = {}
        try:
            if is_git:
                name = plugin_git.split('/')[-1]
            else:
                name = zip_filename.split('.')[0]
            
            plugin_all_path = os.path.join(F.config['path_data'], 'plugins')
            os.makedirs(plugin_all_path, exist_ok=True)
            plugin_path = os.path.join(plugin_all_path, name)
            plugin_info = None
            if os.path.exists(plugin_path):
                ret['ret'] = 'danger'
                ret['msg'] = '이미 설치되어 있습니다.'
                ret['status'] = 'already_exist'
                return ret
            
            if plugin_git and plugin_git.startswith('http'):
                for tag in ['main', 'master']:
                    try:
                        info_url = plugin_git.replace('github.com', 'raw.githubusercontent.com') + f'/{tag}/info.yaml'
                        plugin_info = requests.get(info_url).json()
                        if plugin_info is not None:
                            break
                    except:
                        pass

            if zip_filename and zip_filename != '':
                zip_filepath = os.path.join(F.config['path_data'], 'tmp', zip_filename)
                extract_filepath = os.path.join(F.config['path_data'], 'tmp', name)
                if SupportFile.download(zip_url, zip_filepath):
                    with zipfile.ZipFile(zip_filepath, 'r') as zip_ref:
                        zip_ref.extractall(extract_filepath)
                    plugin_info_filepath = os.path.join(extract_filepath, 'info.yaml')
                    if os.path.exists(plugin_info_filepath):
                        plugin_info = SupportYaml.read_yaml(plugin_info_filepath)
            
            if plugin_info == None:
                plugin_info = {}

            flag = True
            tmp = plugin_info.get('require_os', '')
            if tmp != '' and type(tmp) == type([]) and platform.system() not in tmp:
                ret['ret'] = 'danger'
                ret['msg'] = '설치 가능한 OS가 아닙니다.'
                ret['status'] = 'not_support_os'
                flag = False
            
            tmp = plugin_info.get('require_running_type', '')
            if tmp != '' and type(tmp) == type([]) and F.config['running_type'] not in tmp:
                ret['ret'] = 'danger'
                ret['msg'] = '설치 가능한 실행타입이 아닙니다.'
                ret['status'] = 'not_support_running_type'
                flag = False


            if flag:
                if plugin_git and plugin_git.startswith('http'):
                    command = ['git', '-C', plugin_all_path, 'clone', plugin_git + '.git', '--depth', '1']
                    log = SupportSubprocess.execute_command_return(command, log=True)
                    F.logger.debug(log)
                    if os.path.exists(plugin_path):
                        ret['ret'] = 'success'
                        ret['msg'] = '정상적으로 설치하였습니다. 재시작시 적용됩니다.<br>' + '<br>'.join(log['log'].split('\n'))
                    else:
                        ret['ret'] = 'danger'
                        ret['msg'] = '설치 실패.<br>' + '<br>'.join(log['log'].split('\n'))
                if zip_filename and zip_filename != '':
                    
                    if os.path.exists(plugin_path) == False:
                        shutil.move(extract_filepath, plugin_path)
                    else:
                        for tmp in os.listdir(extract_filepath):
                            shutil.move(os.path.join(extract_filepath, tmp), plugin_path)
                    log = ''

                # 2021-12-31
                tmp = plugin_info.get('require_plugin', '')
                if tmp != '' and type(tmp) == type([]) and len(tmp) > 0:
                    for need_plugin in plugin_info['require_plugin']:
                        if need_plugin['package_name'] in cls.plugin_init:
                            F.logger.debug(f"Dependency 설치 - 이미 설치됨 : {need_plugin['package_name']}")
                            continue
                        else:
                            F.logger.debug(f"Dependency 설치 : {need_plugin['package_name']}")
                            cls.plugin_install(need_plugin['home'], None, None)

                
                #ret['msg'] = '<br>'.join(log)
                   
        except Exception as e: 
            F.logger.error(f'Exception:{str(e)}')
            F.logger.error(traceback.format_exc())
            ret['ret'] = 'danger'
            ret['msg'] = str(e)
        return ret


    @classmethod
    def plugin_update(cls):
        try:
            if os.environ.get('UPDATE_STOP') == 'true':
                return
            if os.environ.get('PLUGIN_UPDATE_FROM_PYTHON') == 'false':
                return
            if F.config['plugin_update'] != True:
                return
            plugins_path = os.path.join(F.config['path_data'], 'plugins')
            if os.path.exists(plugins_path) == False:
                return
            tmps = os.listdir(plugins_path)
            for t in tmps:
                plugin_path = os.path.join(plugins_path, t)
                if t.startswith('_'):
                    continue
                if os.path.exists(os.path.join(plugin_path, '.git')):
                    command = ['git', '-C', plugin_path, 'reset', '--hard', 'HEAD']
                    ret = SupportSubprocess.execute_command_return(command)
                    F.logger.debug(ret)
                    command = ['git', '-C', plugin_path, 'pull']
                    ret = SupportSubprocess.execute_command_return(command)
                    F.logger.debug(ret)
                else:
                    F.logger.debug(f"{plugin_path} not git repo")
        except Exception as e: 
            F.logger.error(f"Exception:{str(e)}")
            F.logger.error(traceback.format_exc())


    @classmethod
    def get_plugin_instance(cls, package_name):
        try:
            if cls.all_package_list[package_name]['loading']:
                return cls.all_package_list[package_name]['P']
        except:
            pass
