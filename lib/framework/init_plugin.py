import os, sys, traceback, threading, platform
from framework import F, d

class PluginManager:
    plugin_list = {}
    plugin_menus = {}
    setting_menus = []


    @classmethod 
    def get_plugin_name_list(cls):
        #if not app.config['config']['auth_status']:
        #    return
        """ 
        plugin_path = os.path.join(frame.config['path_app'], 'plugins')
        sys.path.insert(0, plugin_path)
        from system import SystemModelSetting
        plugins = os.listdir(plugin_path)
        """
        plugins = []
        pass_include = []
        except_plugin_list = []

        #2019-07-17 
        if F.config.get('plugin_loading_only_devpath', None) != True:
            try:
                plugin_path = os.path.join(F.config['path_data'], 'plugins')
                if os.path.exists(plugin_path) == True and os.path.isdir(plugin_path) == True:
                    sys.path.insert(1, plugin_path)
                    tmps = os.listdir(plugin_path)
                    add_plugin_list = []
                    for t in tmps:
                        if not t.startswith('_') and os.path.isdir(os.path.join(plugin_path, t)):
                            add_plugin_list.append(t)
                    plugins = plugins + add_plugin_list
                    pass_include = pass_include + add_plugin_list
            except Exception as exception:
                F.logger.error('Exception:%s', exception)
                F.logger.error(traceback.format_exc())

        # 2018-09-04
        try:
            plugin_path = F.SystemModelSetting.get('plugin_dev_path')
            if plugin_path != '':
                if os.path.exists(plugin_path):
                    sys.path.insert(0, plugin_path)
                    tmps = os.listdir(plugin_path)
                    add_plugin_list = []
                    for t in tmps:
                        if not t.startswith('_')  and os.path.isdir(os.path.join(plugin_path, t)):
                            add_plugin_list.append(t)
                    plugins = plugins + add_plugin_list
                    pass_include = pass_include + add_plugin_list
        except Exception as exception:
            F.logger.error('Exception:%s', exception)
            F.logger.error(traceback.format_exc())

        # plugin_loading_list
        try:
            plugin_loading_list = F.config.get('plugin_loading_list', None)
            if plugin_loading_list != None and type(plugin_loading_list) == type([]):
                new_plugins = []
                for _ in plugins:
                    if _ in plugin_loading_list:
                        new_plugins.append(_)
                plugins = new_plugins
        except Exception as exception:
            F.logger.error('Exception:%s', exception)
            F.logger.error(traceback.format_exc())

        # plugin_except_list
        try:
            plugin_except_list = F.config.get('plugin_except_list', None)
            if plugin_except_list != None and type(plugin_except_list) == type([]):
                new_plugins = []
                for _ in plugins:
                    if _ not in plugin_except_list:
                        new_plugins.append(_)
                plugins = new_plugins
        except Exception as exception:
            F.logger.error('Exception:%s', exception)
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
                 
                #logger.debug(len(system.LogicPlugin.current_loading_plugin_list))
                #if plugin_name.startswith('_'):
                #    continue
                #if plugin_name == 'terminal' and platform.system() == 'Windows':
                #    continue
                #if plugin_name in except_plugin_list:
                #    F.logger.debug('Except plugin : %s' % frame.plugin_menu)
                #    continue
                F.logger.debug(f'[+] PLUGIN LOADING Start.. [{plugin_name}]') 
                entity = {'version':'3'}
                try:
                    mod = __import__('%s' % (plugin_name), fromlist=[])
                    mod_plugin_info = None
                    # 2021-12-31
                    #import system
                    #if plugin_name not in system.LogicPlugin.current_loading_plugin_list:
                    #    system.LogicPlugin.current_loading_plugin_list[plugin_name] = {'status':'loading'}
                     
                    try:
                        mod_plugin_info = getattr(mod, 'plugin_info')
                        entity['module'] = mod 
                        """
                        if 'category'  not in mod_plugin_info and 'category_name' in mod_plugin_info:
                            mod_plugin_info['category'] = mod_plugin_info['category_name']
                        if 'policy_point' in mod_plugin_info:
                            if mod_plugin_info['policy_point'] > app.config['config']['point']:
                                system.LogicPlugin.current_loading_plugin_list[plugin_name]['status'] = 'violation_policy_point'
                                continue
                        if 'policy_level' in mod_plugin_info:
                            if mod_plugin_info['policy_level'] > app.config['config']['level']:
                                system.LogicPlugin.current_loading_plugin_list[plugin_name]['status'] = 'violation_policy_level'
                                continue
                        if 'category' in mod_plugin_info and mod_plugin_info['category'] == 'beta':
                            if SystemModelSetting.get_bool('use_beta') == False:
                                system.LogicPlugin.current_loading_plugin_list[plugin_name]['status'] = 'violation_beta'
                                continue 
                        """
                    except Exception as exception:
                        #logger.error('Exception:%s', exception)
                        #logger.error(traceback.format_exc())  
                        
                        #mod_plugin_info = getattr(mod, 'setup')
                        F.logger.warning(f'[!] PLUGIN_INFO not exist : [{plugin_name}]')  
                    if mod_plugin_info == None:
                        try:
                            mod = __import__(f'{plugin_name}.setup', fromlist=['setup'])
                            entity['version'] = '4'
                        except Exception as e:
                            F.logger.error(f'Exception:{str(e)}')
                            F.logger.error(traceback.format_exc())
                            F.logger.warning(f'[!] NOT normal plugin : [{plugin_name}]')
                            #entity['version'] = 'not_plugin'


                    try:
                        if entity['version'] != '4':
                            mod_blue_print = getattr(mod, 'blueprint')
                            
                        else:
                            entity['setup_mod'] = mod
                            entity['P'] = getattr(mod, 'P')
                            mod_blue_print = getattr(entity['P'], 'blueprint')
                        if mod_blue_print: 
                            #if plugin_name in pass_include or is_include_menu(plugin_name):
                            F.app.register_blueprint(mod_blue_print)
                    except Exception as exception:
                        #logger.error('Exception:%s', exception)
                        #logger.error(traceback.format_exc())
                        F.logger.warning(f'[!] BLUEPRINT not exist : [{plugin_name}]') 
                    cls.plugin_list[plugin_name] = entity
                    #system.LogicPlugin.current_loading_plugin_list[plugin_name]['status'] = 'success'
                    #system.LogicPlugin.current_loading_plugin_list[plugin_name]['info'] = mod_plugin_info
                except Exception as exception:
                    F.logger.error('Exception:%s', exception)
                    F.logger.error(traceback.format_exc())
                    F.logger.debug('no blueprint')
            
            #from tool_base import d 
            #logger.error(d(system.LogicPlugin.current_loading_plugin_list))
            # 2021-07-01 모듈에 있는 DB 테이블 생성이 안되는 문제
            # 기존 구조 : db.create_all() => 모듈 plugin_load => celery task 등록 후 리턴
            # 변경 구조 : 모듈 plugin_load => db.create_all() => celery인 경우 리턴

            # plugin_load 를 해야 하위 로직에 있는 DB가 로딩된다.
            # plugin_load 에 db는 사용하는 코드가 있으면 안된다. (테이블도 없을 때 에러발생)
            try:   
                #logger.warning('module plugin_load in celery ')
                cls.plugin_list['mod']['module'].plugin_load()
            except Exception as exception:
                F.logger.debug(f'mod plugin_load error!!') 
                #logger.error('Exception:%s', exception)
                #logger.error(traceback.format_exc())

            # import가 끝나면 DB를 만든다.
            # 플러그인 로드시 DB 초기화를 할 수 있다.
            if not F.config['run_celery']:
                try: 
                    F.db.create_all()
                except Exception as exception:
                    F.logger.error('Exception:%s', exception)
                    F.logger.error(traceback.format_exc())
                    F.logger.debug('db.create_all error')

            if not F.config['run_flask']:
                # 2021-06-03 
                # 모듈의 로직에 있는 celery 함수는 등록해주어야한다.
                #try:
                #    logger.warning('module plugin_load in celery ')
                #    plugin_instance_list['mod'].plugin_load()
                #except Exception as exception:
                #    logger.error('module plugin_load error')
                #    logger.error('Exception:%s', exception)
                #    logger.error(traceback.format_exc())
                # 2021-07-01
                # db때문에 위에서 로딩함.
                return
            
            for key, entity in cls.plugin_list.items():
                try:
                    mod_plugin_load = None
                    if entity['version'] == '3':
                        mod_plugin_load = getattr(entity['module'], 'plugin_load')
                    elif entity['version'] == '4':
                        mod_plugin_load = getattr(entity['P'], 'plugin_load')
                    #if mod_plugin_load and (key in pass_include or is_include_menu(key)):
                    if mod_plugin_load:
                        def func(mod_plugin_load, key):
                            try:
                                F.logger.debug(f'[!] plugin_load threading start : [{key}]') 
                                #mod.plugin_load()
                                mod_plugin_load()
                                F.logger.debug(f'[!] plugin_load threading end : [{key}]') 
                            except Exception as exception:
                                F.logger.error('### plugin_load exception : %s', key)
                                F.logger.error('Exception:%s', exception)
                                F.logger.error(traceback.format_exc())
                        # mod는 위에서 로딩
                        if key != 'mod':
                            t = threading.Thread(target=func, args=(mod_plugin_load, key))
                            t.setDaemon(True)
                            t.start()
                        #if key == 'mod':
                        #    t.join()
                except Exception as exception:
                    F.logger.debug(f'[!] PLUGIN_LOAD function not exist : [{key}]') 
                    #logger.error('Exception:%s', exception)
                    #logger.error(traceback.format_exc())
                    #logger.debug('no init_scheduler') 
                try:
                    mod_menu = None
                    if entity['version'] == '3':
                        mod_menu = getattr(entity['module'], 'menu')
                    elif entity['version'] == '4':
                        mod_menu = getattr(entity['P'], 'menu')
                    
                    if mod_menu:# and (key in pass_include or is_include_menu(key)):
                        cls.plugin_menus[key]=  {'menu':mod_menu, 'match':False}
                    if entity['version'] == '4':
                        setting_menu = getattr(entity['P'], 'setting_menu')
                        if setting_menu != None:
                            cls.setting_menus.append(setting_menu)

                            
                except Exception as exception:
                    F.logger.debug('no menu')
            F.logger.debug('### plugin_load threading all start.. : %s ', len(cls.plugin_list))
            # 모든 모듈을 로드한 이후에 app 등록, table 생성, start

        except Exception as exception:
            F.logger.error('Exception:%s', exception)
            F.logger.error(traceback.format_exc())



    @classmethod
    def plugin_unload(cls):
        for key, entity in cls.plugin_list.items():
            try:
                if entity['version'] == '3':
                    mod_plugin_unload = getattr(entity['module'], 'plugin_unload')
                elif entity['version'] == '4':
                    mod_plugin_unload = getattr(entity['P'], 'plugin_unload')
                    
                #if plugin_name == 'rss':
                #    continue
                #mod_plugin_unload = getattr(mod, 'plugin_unload')
                if mod_plugin_unload:
                    mod_plugin_unload()
                    #mod.plugin_unload()
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
