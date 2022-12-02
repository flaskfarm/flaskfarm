import traceback

from flask import render_template


class PluginModuleBase(object):
    db_default = None
 
    def __init__(self, P, first_menu=None, name=None, scheduler_desc=None):
        self.P = P
        self.scheduler_desc = scheduler_desc
        self.first_menu = first_menu
        self.name = name
        self.socketio_list = None
        self.page_list = None
        self.web_list_model = None
    
    def get_module(self, module_name):
        try:
            for module in self.P.module_list:
                if module.name == module_name:
                    return module
        except Exception as e:
            self.P.logger.error(f'Exception:{str(e)}')
            self.P.logger.error(traceback.format_exc())


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
            if self.page_list == None:
                return
            for page in self.page_list:
                if page_name == page.name:
                    return page
        except Exception as e:
            self.P.logger.error(f'Exception:{str(e)}')
            self.P.logger.error(traceback.format_exc())


    def process_menu(self, page, req):
        from framework import F
        
        try:
            if self.page_list is not None:
                page_ins = self.get_page(page)
                if page_ins != None:
                    return page_ins.process_menu(req)

            arg = self.P.ModelSetting.to_dict() if self.P.ModelSetting != None else {}
            arg['path_data'] = F.config['path_data']
            arg['is_include'] = F.scheduler.is_include(self.get_scheduler_name())
            arg['is_running'] = F.scheduler.is_running(self.get_scheduler_name())
            return render_template(f'{self.P.package_name}_{self.name}_{page}.html', arg=arg)
        except Exception as e:
            self.P.logger.error(f'Exception:{str(e)}')
            self.P.logger.error(traceback.format_exc())
        return render_template('sample.html', title=f"PluginModuleBase-process_menu{self.P.package_name}/{self.name}/{page}")

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

    def db_delete(self, day):
        if self.web_list_model != None:
            return self.web_list_model.delete_all(day)


    def plugin_load(self):
        pass
    
    def plugin_load_celery(self):
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

    def get_scheduler_id(self):
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


    def arg_to_dict(self, arg):
        return self.P.logic.arg_to_dict(arg)

    def get_scheduler_name(self):
        return f'{self.P.package_name}_{self.name}'


    def process_discord_data(self, data):
        pass

    
    def start_celery(self, func, on_message=None, *args, page=None):
        from framework import F
        if F.config['use_celery']:
            result = func.apply_async(args)
            try:
                if on_message != None:
                    ret = result.get(on_message=on_message, propagate=True)
                else:
                    ret = result.get()
            except:
                ret = result.get()
        else:
            if on_message == None:
                ret = func(*args)
            else:
                if page == None:
                    ret = func(self, *args)
                else:
                    ret = func(page, *args)
        return ret














class PluginPageBase(object):
    db_default = None

    def __init__(self, P, parent, name=None, scheduler_desc=None):
        self.P = P
        self.parent = parent
        self.name = name
        self.scheduler_desc = scheduler_desc
        self.socketio_list = None
        self.web_list_model = None

    def process_menu(self, req):
        try:
            arg = {}
            if self.P.ModelSetting != None:
                arg = self.P.ModelSetting.to_dict()
            return render_template(f'{self.P.package_name}_{self.parent.name}_{self.name}.html', arg=arg)
        except Exception as e:
            self.P.logger.error(f'Exception:{str(e)}')
            self.P.logger.error(traceback.format_exc())
            
        return render_template('sample.html', title=f"PluginPageBase-process_menu --- {self.P.package_name}/{self.parent.name}/{self.name}")


    def process_ajax(self, sub, req):
        pass
    
    def process_api(self, sub, req):
        pass

    def process_normal(self, sub, req):
        pass
    
    def process_command(self, command, arg1, arg2, arg3, req):
        pass
    
    
    
    # logic
    def plugin_load(self):
        pass
    
    def plugin_load_celery(self):
        pass
    
    # logic
    def plugin_unload(self):
        pass

    def scheduler_function(self):
        pass

    def get_scheduler_desc(self):
        return self.scheduler_desc 
    
    def get_scheduler_interval(self):
        if self.P is not None and self.P.ModelSetting is not None and self.parent.name is not None and self.name is not None:
            return self.P.ModelSetting.get(f'{self.parent.name}_{self.name}_interval')

    def get_scheduler_name(self):
        return f'{self.P.package_name}_{self.parent.name}_{self.name}'


    # logic
    def migration(self):
        pass

    
    # route
    def setting_save_after(self, change_list):
        pass

    def process_telegram_data(self, data, target=None):
        pass


    def arg_to_dict(self, arg):
        return self.P.logic.arg_to_dict(arg)


    def get_page(self, page_name):
        return self.parent.get_page(page_name)


    def get_module(self, module_name):
        return self.parent.get_module(module_name)

    def process_discord_data(self, data):
        pass
    
    def db_delete(self, day):
        if self.web_list_model != None:
            return self.web_list_model.delete_all(day)
    

    def start_celery(self, func, on_message, *args):
        return self.parent.start_celery(func, on_message, *args, page=self)
    
    """
    def start_celery(self, func, on_message=None, *args):
        from framework import F
        if F.config['use_celery']:
            result = func.apply_async(args)
            try:
                if on_message != None:
                    ret = result.get(on_message=on_message, propagate=True)
                else:
                    ret = result.get()
            except:
                ret = result.get()
        else:
            ret = func(*args)
        return ret
    """