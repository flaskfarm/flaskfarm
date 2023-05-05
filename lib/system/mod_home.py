import platform

from support import SupportUtil

from .setup import *

name = 'home'

class ModuleHome(PluginModuleBase):
    info_thread = None 

    def __init__(self, P):
        super(ModuleHome, self).__init__(P, name=name)
        default_route_socketio_module(self)

    def process_menu(self, page, req):
        arg = {'changelog':F.config['DEFINE']['CHANGELOG']}
        return render_template(f'{__package__}_{name}.html', info=self.get_info('static'), arg=arg)

    def process_command(self, command, arg1, arg2, arg3, req):
        if command == 'recent_version':
            result = F.get_recent_version()
            if result:
                #F.config['recent_version'] = '4.0.0'
                ret = {'msg': f"최신버전 : {F.config['recent_version']}", 'type':'success'}
            else:
                ret = {'msg': f"확인 실패", 'type':'warning'}
            return jsonify(ret)
        elif command == 'get_config':
            data = {}
            for key, value in F.app.config.items():
                if key not in ['SECRET_KEY']:
                    data[key] = str(value)
            ret = {'json':{'Framework':F.config, 'Flask':data}, 'title':'config'}
            return jsonify(ret)
       

    def socketio_connect(self):
        self.send_info()
        if self.info_thread != None:
            return

        def func():
            while True:
                if len(self.socketio_list) == 0:
                    break
                self.send_info()
                time.sleep(1)
            self.info_thread = None

        self.info_thread = threading.Thread(target=func, args=())
        self.info_thread.daemon = True
        self.info_thread.start()

    def send_info(self):
        ret = {}
        ret['system'] = self.get_info()
        ret['scheduler'] = scheduler.get_job_list_info()
        F.socketio.emit("status", ret, namespace=f'/{P.package_name}/{name}')
    
    
    def get_info(self, mode=''):
        info = {}
        if mode == 'static':
            info['platform'] = platform.platform()
            info['processor'] = platform.processor()

            info['python_version'] = sys.version
            info['version'] = VERSION
            info['recent_version'] = F.config['recent_version']
            info['path_app'] = F.config['path_app']
            info['path_data'] = F.config['path_data']
            info['path_working'] = F.config['path_working']
            info['config_filepath'] = F.config['config_filepath']
            info['running_type'] = F.config['running_type'] 
            info['use_celery'] = '사용' if F.config['use_celery'] else '미사용'
        else:
            info['version'] = VERSION
            info['recent_version'] = F.config['recent_version']
            #info['auth'] = frame.config['member']['auth_desc']
            info['cpu_percent'] = 'not supported'
            info['memory'] = 'not supported'
            info['disk'] = 'not supported'
            if frame.config['running_type'] != 'termux':
                try:
                    import psutil
                    info['cpu_percent'] = '%s %%' % psutil.cpu_percent() 
                    tmp = psutil.virtual_memory()
                    info['memory'] = [
                        SupportUtil.sizeof_fmt(tmp[0], suffix='B'),
                        SupportUtil.sizeof_fmt(tmp[3], suffix='B'),
                        SupportUtil.sizeof_fmt(tmp[1], suffix='B'),
                        tmp[2]
                    ]
                except:
                    pass

                try:
                    if platform.system() == 'Windows':
                        s = os.path.splitdrive(path_app_root)
                        root = s[0]
                    else:
                        root = '/'
                    tmp = psutil.disk_usage(root)
                    info['disk'] = [
                        SupportUtil.sizeof_fmt(tmp[0], suffix='B'), 
                        SupportUtil.sizeof_fmt(tmp[1], suffix='B'), 
                        SupportUtil.sizeof_fmt(tmp[2], suffix='B'), 
                        tmp[3], root]
                except Exception as exception: 
                    pass
            try:
                system_start_time = SystemModelSetting.get('system_start_time')
                timedelta = datetime.now() - datetime.strptime(system_start_time, '%Y-%m-%d %H:%M:%S')
                info['time'] = [
                    system_start_time,
                    str(timedelta).split('.')[0],
                    F.config['arg_repeat']
                ]
            except Exception as exception: 
                info['time'] = str(exception)
        return info
