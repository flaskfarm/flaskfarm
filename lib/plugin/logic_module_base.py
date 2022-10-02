import traceback

class PluginModuleBase(object):
    db_default = None
 
    def __init__(self, P, first_menu=None, name=None, scheduler_desc=None):
        self.P = P
        self.scheduler_desc = scheduler_desc
        self.first_menu = first_menu
        self.name = name
        self.socketio_list = None
        self.page_list = None
    
    # set_module_list 대응
    def set_page_list(self, page_list):
        try:
            self.page_list = []
            for mod in page_list:
                mod_ins = mod(self.P, self)
                self.page_list.append(mod_ins)
            
        except Exception as e:
            self.P.logger.error(f'Exception:{str(e)}')
            self.P.logger.error(traceback.format_exc())
    
    def get_page(self, page_name):
        try:
            for page in self.page_list:
                if page_name == page.name:
                    return page
        except Exception as e:
            self.P.logger.error(f'Exception:{str(e)}')
            self.P.logger.error(traceback.format_exc())


    def process_menu(self, sub):
        pass

    def process_ajax(self, sub, req):
        pass

    def process_command(self, command, arg1, arg2, arg3, req):
        pass

    def process_api(self, sub, req):
        pass

    def process_normal(self, sub, req):
        pass

    def scheduler_function(self):
        pass

    def reset_db(self):
        pass

    def plugin_load(self):
        pass
    
    def plugin_unload(self):
        pass
    
    def setting_save_after(self, change_list):
        pass

    def process_telegram_data(self, data, target=None):
        pass

    def migration(self):
        pass
    
    #################################################################
    def get_scheduler_desc(self):
        return self.scheduler_desc 

    def get_scheduler_interval(self):
        if self.P is not None and self.P.ModelSetting is not None and self.name is not None:
            return self.P.ModelSetting.get('{module_name}_interval'.format(module_name=self.name))

    def get_first_menu(self):
        return self.first_menu

    def get_scheduler_name(self):
        return '%s_%s' % (self.P.package_name, self.name)

    def dump(self, data):
        if type(data) in [type({}), type([])]:
            import json
            return '\n' + json.dumps(data, indent=4, ensure_ascii=False)
        else:
            return str(data)

    def socketio_connect(self):
        pass

    def socketio_disconnect(self):
        pass


class PluginPageBase(object):
    db_default = None

    def __init__(self, P, parent, name=None, scheduler_desc=None):
        self.P = P
        self.parent = parent
        self.name = name
        self.scheduler_desc = scheduler_desc
        self.socketio_list = None


    def process_ajax(self, sub, req):
        pass

    def scheduler_function(self):
        pass
    
    def plugin_load(self):
        pass
    
    def plugin_unload(self):
        pass


    def get_scheduler_desc(self):
        return self.scheduler_desc 
    
    def get_scheduler_interval(self):
        if self.P is not None and self.P.ModelSetting is not None and self.parent.name is not None and self.name is not None:
            return self.P.ModelSetting.get(f'{self.parent.name}_{self.name}_interval')

    def get_scheduler_name(self):
        return f'{self.P.package_name}_{self.parent.name}_{self.name}'









    
    
    def process_api(self, sub, req):
        pass

    def process_normal(self, sub, req):
        pass

    

    def reset_db(self):
        pass

    
    
    def setting_save_after(self, change_list):
        pass

    def process_telegram_data(self, data, target=None):
        pass

    def migration(self):
        pass
    
    #################################################################
    

    def process_menu(self, sub):
        pass

