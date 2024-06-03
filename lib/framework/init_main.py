import logging
import logging.handlers
import os
import platform
import shutil
import sys
import time
import traceback
from datetime import datetime

import yaml
from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager, login_required
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from pytz import timezone, utc

from .init_declare import CustomFormatter, check_api


class Framework:
    __instance = None

    @classmethod
    def get_instance(cls):
        if cls.__instance == None:
            cls.__instance = Framework()
        return cls.__instance


    def __init__(self):
        self.logger = None
        self.app = None
        self.celery = None
        self.db = None
        self.scheduler = None
        self.socketio = None
        self.path_app_root = None
        self.path_data = None
        self.users = {}

        self.__level_unset_logger_list = []
        self.__logger_list = []
        self.__exit_code = -1
        self.login_manager = None
        #self.plugin_instance_list = {}
        #self.plugin_menus = {}
        
        # 그냥 F. 로 접근 하게....
        self.SystemModelSetting = None
        self.Job = None
        self.login_required = login_required
        self.check_api = check_api
        self.__initialize()
     

    def __initialize(self):
        os.environ["PYTHONUNBUFFERED"] = "1"
        os.environ['FF'] = "true"
        os.environ['FF_PYTHON'] = sys.executable
        self.__config_initialize("first")
        self.__make_default_dir()
        
        self.logger = self.get_logger(__package__)
        import support

        self.__prepare_starting()
        self.app = Flask(__name__)
        self.__config_initialize('flask')

        self.__init_db()
        
        if True or self.config['run_flask']:
            from .scheduler import Job, Scheduler
            self.scheduler = Scheduler(self)
            self.Job = Job

        if self.config['use_gevent']:
            self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        else:
            self.socketio = SocketIO(self.app, cors_allowed_origins="*", async_mode='threading')
        
        CORS(self.app)

        self.login_manager = LoginManager()
        self.login_manager.init_app(self.app)
        self.login_manager.login_view = "/system/login"
        
        self.celery = self.__init_celery()
        
        from flask_dropzone import Dropzone
        self.app.config.update(
            DROPZONE_MAX_FILE_SIZE = 102400,
            DROPZONE_TIMEOUT = 5*60*1000,
            DROPZONE_ALLOWED_FILE_CUSTOM = True,
            DROPZONE_ALLOWED_FILE_TYPE = "image/*, audio/*, video/*, text/*, application/*, *.*",
        )
        self.dropzone = Dropzone(self.app)


    def __init_db(self):
        # https://flask-sqlalchemy.palletsprojects.com/en/3.0.x/config/#flask_sqlalchemy.config.SQLALCHEMY_BINDS
        # 어떤 편법도 불가. db를 사용하지 않아도 파일이 생김.
        db_path = os.path.join(self.config['path_data'], 'db', 'system.db')
        self.app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}?check_same_thread=False' # 3.0에서 필수
        self.app.config['SQLALCHEMY_BINDS'] = {'system':f'sqlite:///{db_path}?check_same_thread=False'}
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        _ = os.path.join(self.config['path_data'], 'plugins')
        plugins = []
        if os.path.exists(_):
            plugins = os.listdir(_)
        
        if self.config['path_dev'] != None:
            if type(self.config['path_dev']) == type(''):
                plugin_path_list = [self.config['path_dev']]
            elif type(self.config['path_dev']) == type([]):
                plugin_path_list = self.config['path_dev']
            for __ in plugin_path_list:
                if os.path.exists(__):
                    plugins += os.listdir(__)
        
        for package_name in plugins:
            db_path = os.path.join(self.config['path_data'], 'db', f'{package_name}.db')
            self.app.config['SQLALCHEMY_BINDS'][package_name] = f'sqlite:///{db_path}?check_same_thread=False'
        self.db = SQLAlchemy(self.app, session_options={"autoflush": False, "expire_on_commit": False})  
        #with self.app.app_context():
        #    self.db.session.expunge_all()

        
    def __init_celery(self):
        try:
            from celery import Celery

            #if frame.config['use_celery'] == False or platform.system() == 'Windows':
            if self.config['use_celery'] == False:
                raise Exception('no celery')
            
            redis_port = os.environ.get('REDIS_PORT', None)
            if redis_port == None:
                redis_port = self.config.get('redis_port', None)
            if redis_port == None:
                redis_port = '6379'
  

            self.app.config['CELERY_BROKER_URL'] = 'redis://localhost:%s/0' % redis_port
            self.app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:%s/0' % redis_port
            celery = Celery(self.app.name, broker=self.app.config['CELERY_BROKER_URL'], backend=self.app.config['CELERY_RESULT_BACKEND'])
            celery.conf['CELERY_ENABLE_UTC'] = False
            celery.conf.update(
                task_serializer='pickle',
                result_serializer='pickle',
                accept_content=['pickle'],
                timezone='Asia/Seoul'
            )
            from celery import bootsteps
            from click import Option
            celery.user_options['worker'].add(Option(('--config_filepath',), help=''),)
            celery.user_options['worker'].add(Option(('--running_type',), help=''),)
            class CustomArgs(bootsteps.Step):
                def __init__(self, worker, config_filepath=None, running_type=None,  **options):
                    from . import F
                    F.logger.info(f"celery config_filepath: {config_filepath}")
                    F.logger.info(f"celery running_type: {running_type}")
                    #F.logger.info(f"celery running_type: {options}")
            celery.steps['worker'].add(CustomArgs)
        except Exception as e:
            if self.config['use_celery']:
                self.logger.error('CELERY!!!')
                self.logger.error(f'Exception:{str(e)}')
                self.logger.error(traceback.format_exc())
            else:
                self.logger.info("use_celery = False")

            def dummy_func():
                pass
                    
            class celery(object):
                class task(object):
                    def __init__(self, *args, **kwargs):
                        if len(args) > 0:
                            self.f = args[0]
                
                    def __call__(self, *args, **kwargs):
                        if len(args) > 0 and type(args[0]) == type(dummy_func):
                            return args[0]
                        self.f(*args, **kwargs)
        return celery


    def initialize_system(self):
        from system.setup import P
        SystemInstance = P
        try:
            with self.app.app_context():
                self.db.create_all()
        except Exception as e:
            self.logger.error('CRITICAL db.create_all()!!!')
            self.logger.error(f'Exception:{str(e)}')
            self.logger.error(traceback.format_exc())
        self.SystemModelSetting = SystemInstance.ModelSetting 
        if self.config['run_flask']:
            SystemInstance.plugin_load()
        self.app.register_blueprint(SystemInstance.blueprint)
        self.config['flag_system_loading'] = True
        self.__config_initialize('member')
        self.__config_initialize('system_loading_after')
        self.set_level(self.SystemModelSetting.get_int('log_level'))
       

    def initialize_plugin(self): 
        from system.setup import P as SP

        from .init_web import jinja_initialize
        jinja_initialize(self.app)
        
        from .init_plugin import PluginManager
        self.PluginManager = PluginManager
        PluginManager.plugin_update()
        PluginManager.plugin_init()
        PluginManager.plugin_menus['system'] = {'menu':SP.menu, 'match':False} 

        from .init_menu import MenuManager
        MenuManager.init_menu()
        self.logger.info("메뉴 구성 완료")

        if self.config['run_flask']:
            if self.config.get('port') == None:
                self.config['port'] = self.SystemModelSetting.get_int('port')

        from . import init_route, log_viewer

        self.__make_default_logger()
        self.__config_initialize("last")
        self.logger.info('### LAST')
        self.logger.info(f"### PORT: {self.config.get('port')}")
        self.logger.info('### Now you can access App by webbrowser!!')


    def __prepare_starting(self):
        # 여기서 monkey.patch시 너무 늦다고 문제 발생
        pass
        
        
    ###################################################
    # 환경
    ###################################################
    def __config_initialize(self, mode):
        if mode == "first":
            self.config = {}
            self.config['os'] = platform.system()
            self.config['flag_system_loading'] = False
            #self.config['run_flask'] = True if sys.argv[0].endswith('main.py') else False
            self.config['run_celery'] = True if sys.argv[0].find('celery') != -1 else False
            self.config['run_flask'] = not self.config['run_celery']
            self.config['path_app'] = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            if self.config['os'] == 'Windows' and self.config['path_app'][0] != '/':
                self.config['path_app'] = self.config['path_app'][0].upper() + self.config['path_app'][1:]
            self.path_app_root = self.config['path_app']
            self.config['path_working'] = os.getcwd()
            if os.environ.get('RUNNING_TYPE', None) != None:
                self.config['running_type'] = os.environ.get('RUNNING_TYPE')
            self.config['export_filepath'] = os.path.join(self.config['path_app'], 'export.sh')
            self.config['exist_export'] = os.path.exists(self.config['export_filepath'])
            self.config['recent_version'] = '--'
            from .version import VERSION
            self.config['version'] = VERSION
            self.__process_args()
            self.__load_config()
            self.__init_define()
            self.config['menu_yaml_filepath'] = os.path.join(self.config['path_data'], 'db', 'menu.yaml')
            self.config['notify_yaml_filepath'] = os.path.join(self.config['path_data'], 'db', 'notify.yaml')
            if 'running_type' not in self.config:
                self.config['running_type'] = 'native'
            self.pip_install()
        elif mode == "flask":
            self.app.secret_key = os.urandom(24)
            self.app.config['TEMPLATES_AUTO_RELOAD'] = True
            self.app.config['JSON_AS_ASCII'] = False
        elif mode == 'system_loading_after':
            pass
        elif mode == 'last':
            db_foder = os.path.join(self.config['path_data'], 'db')
            for name in os.listdir(db_foder):
                if name.endswith('.db'):
                    db_filepath = os.path.join(db_foder, name)
                    try:
                        if os.stat(db_filepath).st_size == 0:
                            os.remove(db_filepath)
                            self.logger.debug(f"REMOVE {db_filepath}")
                    except:
                        pass



    def __init_define(self):
        self.config['DEFINE'] = {}
        # 이건 필요 없음
        self.config['DEFINE']['GIT_VERSION_URL'] = 'https://raw.githubusercontent.com/flaskfarm/flaskfarm/main/lib/framework/version.py'
        self.config['DEFINE']['CHANGELOG'] = 'https://github.com/flaskfarm/flaskfarm'
        self.config['DEFINE']['WEB_DIRECT_URL'] = "http://52.78.103.230:49734"


    def __process_args(self):
        # celery 에서 args 처리시 문제 발생.
        if self.config['run_flask']:
            import argparse
            parser = argparse.ArgumentParser()
            parser.add_argument('--config', default='.', help='config filepath. Default: {current folder}/config.yaml')
            parser.add_argument('--repeat', default=0, type=int, help=u'Do not set. This value is set by automatic')
            args = parser.parse_args()
            self.config['arg_repeat'] = args.repeat
            self.config['arg_config'] = args.config
        else:
            # 아주 안좋은 구조..
            # celery user_options으로 configfilepath를 받은 후 처리해야하나, 로그파일 경로 등에서 데이터 폴더 위치를 미리 사용하는 경우가 많다.
            # sys.argv에서 데이터 경로를 바로 가져와서 사용.
            self.config['arg_repeat'] = 0
            #self.config['arg_config'] = sys.argv[-1].split('=')[-1]
            #self.config['arg_config'] = sys.argv[-1].split('=')[-1]
            for tmp in sys.argv:
                if tmp.startswith('--config_filepath'):
                    self.config['arg_config'] = tmp.split('=')[1]
                    #break
                elif tmp.startswith('--running_type'):
                    self.config['running_type'] = tmp.split('=')[1]

            #self.config['arg_config'] = 

    def __load_config(self):
        #if self.config['run_flask']:
        if self.config['arg_config'] == '.':
            #self.config['config_filepath'] = os.path.join(self.path_app_root, 'config.yaml')
            self.config['config_filepath'] = os.path.join(self.config['path_working'], 'config.yaml')
        else:
            self.config['config_filepath'] = self.config['arg_config']
        if os.path.exists(self.config['config_filepath']) == False:
            if self.config.get('running_type', '').startswith('docker'):
                with open(self.config['config_filepath'], 'w', encoding='utf8') as f:
                    yaml.dump({'path_data':'/data'}, f, default_flow_style=False, allow_unicode=True)
            else:                
                shutil.copy(
                    os.path.join(self.path_app_root, 'files', 'config.yaml.template'),
                    self.config['config_filepath']
                )
        with open(self.config['config_filepath'], encoding='utf8') as file:
            data = yaml.load(file, Loader=yaml.FullLoader)
        for key, value in data.items():
            if key == 'running_type' and value not in ['termux', 'entware']:
                continue
            self.config[key] = value

        if self.config['path_data'] == '.':
            self.config['path_data'] = self.config['path_working']
            # 예외적으로 현재폴더가 app일 경우 지저분해지는 것을 방지하기 위해 data 로 지정
            if self.config['path_data'] == self.config['path_working']:
                self.config['path_data'] = os.path.join(self.config['path_working'], 'data')
        self.path_data = self.config['path_data'] 

        if self.config.get('use_gevent') == None:
            self.config['use_gevent'] = True
        if self.config.get('use_celery') == None:
            self.config['use_celery'] = True
        if self.config.get('debug') == None:
            self.config['debug'] = False
        if self.config.get('plugin_update') == None:
            self.config['plugin_update'] = True
        # 2022-11-20
        if self.config['debug']:
            self.config['plugin_update'] = False
        if self.config.get('plugin_loading_only_devpath') == None:
            self.config['plugin_loading_only_devpath'] = False
        if self.config.get('plugin_loading_list') == None:
            self.config['plugin_loading_list'] = []
        if self.config.get('plugin_except_list') == None:
            self.config['plugin_except_list'] = []
        if self.config.get('path_dev') == None:
            self.config['path_dev'] = None
        

    def __make_default_dir(self):
        os.makedirs(self.config['path_data'], exist_ok=True)
        tmp = os.path.join(self.config['path_data'], 'tmp')
        try:
            import shutil
            if os.path.exists(tmp):
                shutil.rmtree(tmp)
        except:
            pass
        sub = ['db', 'log', 'tmp']
        for item in sub:
            tmp = os.path.join(self.config['path_data'], item)
            os.makedirs(tmp, exist_ok=True)
        
    ###################################################



    
    ###################################################
    # 로그
    ###################################################
    def get_logger(self, name, from_command=False):
        logger = logging.getLogger(name)
        if not logger.handlers:
            level = logging.DEBUG
            try:
                if self.config['flag_system_loading']:
                    try:
                        #from system import SystemModelSetting
                        level = self.SystemModelSetting.get_int('log_level')
                    except:
                        level = logging.DEBUG
                    if self.__level_unset_logger_list is not None:
                        for item in self.__level_unset_logger_list:
                            item.setLevel(level)
                        self.__level_unset_logger_list = None
                else:
                    self.__level_unset_logger_list.append(logger)
                if name.startswith('apscheduler'):
                    level = logging.CRITICAL
                else:
                    self.__logger_list.append(logger)
            except:
                pass
            logger.setLevel(level)
            def customTime(*args):
                utc_dt = utc.localize(datetime.utcnow())
                my_tz = timezone("Asia/Seoul")
                converted = utc_dt.astimezone(my_tz) 
                return converted.timetuple()

            if from_command == False:
                file_formatter = logging.Formatter(u'[%(asctime)s|%(levelname)s|%(filename)s:%(lineno)s] %(message)s')
            else:
                file_formatter = logging.Formatter(u'[%(asctime)s] %(message)s')

            file_formatter.converter = customTime
            file_max_bytes = 1 * 1024 * 1024 
            fileHandler = logging.handlers.RotatingFileHandler(filename=os.path.join(self.path_data, 'log', f'{name}.log'), maxBytes=file_max_bytes, backupCount=5, encoding='utf8', delay=True)
            fileHandler.setFormatter(file_formatter) 
            logger.addHandler(fileHandler)
            if from_command == False:
                streamHandler = logging.StreamHandler() 
                streamHandler.setFormatter(CustomFormatter()) 
                logger.addHandler(streamHandler)
        return logger 


    def __make_default_logger(self):
        self.get_logger('apscheduler.scheduler')
        self.get_logger('apscheduler.executors.default')
        try: logging.getLogger('socketio').setLevel(logging.ERROR)
        except: pass
        try: logging.getLogger('engineio').setLevel(logging.ERROR)
        except: pass
        try: logging.getLogger('apscheduler.scheduler').setLevel(logging.ERROR)
        except: pass
        try: logging.getLogger('apscheduler.executors.default').setLevel(logging.ERROR)
        except: pass
        try: logging.getLogger('werkzeug').setLevel(logging.ERROR)
        except: pass

    def set_level(self, level):
        try:
            for l in self.__logger_list:
                l.setLevel(int(level))
            self.__make_default_logger()
        except:
            pass    
    ###################################################
    

    def start(self):
        host = '0.0.0.0'
        for i in range(5): 
            try: 
                #self.logger.debug(d(self.config))
                # allow_unsafe_werkzeug=True termux  nohup 실행시 필요함
                #if self.config['running_type'] == 'termux':
                #    self.socketio.run(self.app, host=host, port=self.config['port'], debug=self.config['debug'], use_reloader=self.config['debug'], allow_unsafe_werkzeug=True)
                #else:
                self.socketio.run(self.app, host=host, port=self.config['port'], debug=self.config['debug'], use_reloader=self.config['debug'])
                self.logger.warning(f"EXIT CODE : {self.__exit_code}")
                # 2021-05-18  
                if self.config['running_type'] in ['termux', 'entware']:
                    os._exit(self.__exit_code)
                else:
                    if self.__exit_code != -1:
                        sys.exit(self.__exit_code)
                    else:
                        self.logger.warning(f"framework.exit_code is -1")
                break
            except Exception as exception:
                self.logger.error(f"Start ERROR : {str(exception)}")
                host = '127.0.0.1'  
                time.sleep(10*i)
                continue  
            except KeyboardInterrupt: 
                self.logger.error('KeyboardInterrupt !!')
            
                
            #except SystemExit: 
            #    return 
                #sys.exit(self.__exit_code)


    # system 플러그인에서 콜
    def restart(self):
        self.__exit_code = 1
        self.__app_close()

    def shutdown(self):
        self.__exit_code = 0
        self.__app_close()

    def __app_close(self):
        try:
            from support import SupportSubprocess
            SupportSubprocess.all_process_close()
            from .init_plugin import PluginManager
            PluginManager.plugin_unload()
            with self.app.test_request_context():
                self.socketio.stop()
        except Exception as e: 
            self.logger.error(f"Exception:{str(e)}")
            self.logger.error(traceback.format_exc())

    def get_recent_version(self):
        try:
            import requests
            text = requests.get(self.config['DEFINE']['GIT_VERSION_URL']).text
            self.config['recent_version'] = text.split('=')[1].strip().strip('"')
            return True
        except Exception as e:
            self.logger.error(f'Exception:{str(e)}')
            self.logger.error(traceback.format_exc())
            self.config['recent_version'] =  '확인 실패'
        return False        


    # dev 도커용. package는 setup에 포함.
    def pip_install(self):
        try:
            import json_fix
        except:
            os.system('pip install json_fix')
