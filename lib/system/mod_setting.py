import random, string

from .setup import *

name = 'setting'

class ModuleSetting(PluginModuleBase):
    db_default = {
        'db_version' : '1',
        'port' : '9999',
        'ddns' : 'http://localhost:9999',
        'use_login' : 'False',
        'web_id': 'admin',
        'web_pw': 'Vm51JgZqhpwXc/UPc9CAN1lhj4s65+4ikv7GzNmvN6c=',
        'web_title': 'Home',
        'use_apikey': 'False',
        'apikey': ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10)),
        
        f'restart_interval': f'{random.randint(0,59)} {random.randint(1,23)} * * *',

        'theme' : 'Cerulean',
        'log_level' : '20',
        'plugin_dev_path': os.path.join(F.config['path_data'], 'dev'),

        'system_start_time': '',
    }

    def __init__(self, P):
        super(ModuleSetting, self).__init__(P, name=name, first_menu='basic')
        

    def process_menu(self, page, req):
        arg = P.ModelSetting.to_dict()
        try:
            return render_template(f'{__package__}_{name}_{page}.html', arg=arg)
        except Exception as e: 
            P.logger.error(f'Exception:{str(e)}')
            P.logger.error(traceback.format_exc())
            return render_template('sample.html', title=f"{__package__}/{name}/{page}")

    def process_command(self, command, arg1, arg2, arg3, req):
        if command == 'apikey_generate':
            return jsonify(''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10)))
            

    def plugin_load(self):
        try:
            if F.config['arg_repeat'] == 0 or SystemModelSetting.get('system_start_time') == '':
                SystemModelSetting.set('system_start_time', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            SystemModelSetting.set('repeat', str(F.config['arg_repeat']))
            username = SystemModelSetting.get('web_id')
            passwd = SystemModelSetting.get('web_pw')
            F.users[username] = User(username, passwd_hash=passwd)

            self.__set_restart_scheduler()
            self.__set_scheduler_check_scheduler()
            F.get_recent_version()
        except Exception as e:
            P.logger.error(f'Exception:{str(e)}')
            P.logger.error(traceback.format_exc())
    
    def setting_save_after(self, change_list):
        if 'theme'  in change_list:
            F.socketio.emit("refresh", {}, namespace='/framework', broadcast=True)
         



    
    def __set_restart_scheduler(self):
        name = f'{__package__}_restart'
        if F.scheduler.is_include(name):
            F.scheduler.remove_job(name)
        interval = SystemModelSetting.get('restart_interval')
        if interval != '0':
            if len(interval.split(' ')) == 1:
                interval = '%s' % (int(interval) * 60)
            job_instance = Job(__package__, name, interval, F.restart, "자동 재시작")
            F.scheduler.add_job_instance(job_instance, run=False)


    def __set_scheduler_check_scheduler(self):
        name = 'scheduler_check'
        if F.scheduler.is_include(name):
            F.scheduler.remove_job(name)

        job_instance = Job(__package__, name, 2, F.scheduler.first_run_check_thread_function, "Scheduler Check")
        scheduler.add_job_instance(job_instance, run=False)


    
