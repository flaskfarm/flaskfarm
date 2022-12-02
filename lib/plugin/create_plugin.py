import os
import traceback

from flask import Blueprint
from framework import F
from support import SupportYaml

from . import (Logic, default_route, default_route_single_module,
               get_model_setting)


class PluginBase(object):
    package_name = None
    logger = None
    blueprint = None
    menu = None
    plugin_info = None
    ModelSetting = None
    logic = None
    module_list = None
    home_module = None
    vars = []

    def __init__(self, setting):
        try:
            is_system = ('system' == os.path.basename(os.path.dirname(setting['filepath'])))
            self.status = ""
            self.setting = setting

            info_filepath = os.path.join(os.path.dirname(setting['filepath']), 'info.yaml')
            if os.path.exists(info_filepath) == False and is_system == False:
                return
            if is_system:
                self.package_name = 'system'
            else:
                self.plugin_info = SupportYaml.read_yaml(info_filepath)
                self.package_name = self.plugin_info['package_name']

            self.logger = F.get_logger(self.package_name)
            self.blueprint = Blueprint(self.package_name, self.package_name, url_prefix=f'/{self.package_name}', template_folder=os.path.join(os.path.dirname(setting['filepath']), 'templates'), static_folder=os.path.join(os.path.dirname(setting['filepath']), 'static'))
            self.menu = setting['menu']
            self.setting_menu = setting.get('setting_menu', None)

            self.ModelSetting = None
            if setting.get('use_db', True):
                db_path = os.path.join(F.config['path_data'], 'db', f'{self.package_name}.db')
                F.app.config['SQLALCHEMY_BINDS'][self.package_name] = f"sqlite:///{db_path}?check_same_thread=False"
            if setting.get('use_default_setting', True):
                self.ModelSetting = get_model_setting(self.package_name, self.logger)
            
            self.module_list = []
            self.home_module = setting.get('home_module')
            self.status = "init_success"
            self.config = {}
        except Exception as e: 
            self.logger.error(f'Exception:{str(e)}')
            self.logger.error(traceback.format_exc())
            self.status = 'init_fail'

    def set_module_list(self, mod_list):
        try:
            for mod in mod_list:
                mod_ins = mod(self)
                self.module_list.append(mod_ins)
            if self.home_module == None:
                self.home_module = self.module_list[0].name
        except Exception as e:
            F.logger.error(f'[{self.package_name}] Exception:{str(e)}')
            F.logger.error(traceback.format_exc())

            
        self.logic = Logic(self)
        route_mode = self.setting.get('default_route', 'normal')
        if route_mode == 'normal':
            default_route(self)
        elif route_mode == 'single':
            default_route_single_module(self)


    def plugin_load(self):
        if self.logic:
            self.logic.plugin_load()
    
    def plugin_load_celery(self):
        if self.logic:
            self.logic.plugin_load_celery()

    
    def plugin_unload(self):
        if self.logic:
            self.logic.plugin_unload()

    def get_first_manual_path(self):
        for __ in self.menu['list']:
            if __['uri'] == 'manual' and len(__['list']) > 0:
                return __['list'][0]['uri']


def create_plugin_instance(config):
    ins = PluginBase(config)
    return ins
