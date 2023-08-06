import queue
import shlex

from support import SupportSubprocess
from tool import ToolModalCommand

from .setup import *


class PageCommand(PluginPageBase):
    
    def __init__(self, P, parent):
        super(PageCommand, self).__init__(P, parent, name='command')
        self.db_default = {
            f'{self.parent.name}_{self.name}_recent': '',
        } 

    def process_menu(self, req):
        arg = self.P.ModelSetting.to_dict()
        arg['path_data'] = F.config['path_data']
        return render_template(f'{self.P.package_name}_{self.parent.name}_{self.name}.html', arg=arg)
        


    def process_command(self, command, arg1, arg2, arg3, req):
        ret = {'ret':'success'}
        if command == 'foreground_command':
            P.ModelSetting.set(f'{self.parent.name}_{self.name}_recent', arg1)
            self.__foreground_execute(arg1, shlex.split(arg1))
            
            return jsonify('')
        elif command == 'job_new':
            db_item = ModelCommand.job_new(arg1)
            ret['msg'] = f"ID:{db_item.id} 작업을 생성하였습니다." 
        elif command == 'job_list':
            ret['data'] = ModelCommand.job_list()
            
        elif command == 'job_save':
            data = P.logic.arg_to_dict(arg1)
            db_item = ModelCommand.get_by_id(data['job_id'])
            db_item.set_command(data['job_command'])
            db_item.args = data['job_command_args']
            db_item.description = data['job_description']
            db_item.schedule_mode = data['job_schedule_mode']
            db_item.schedule_auto_start = (data.get('job_schedule_auto_start', 'False') == 'True')
            db_item.schedule_interval = data.get('job_schedule_interval', '')
            db_item.save()
            ret['msg'] = '수정하였습니다.'
        elif command == 'job_remove':
            if ModelCommand.delete_by_id(arg1):
                ret['msg'] = '삭제하였습니다.'
            else:
                ret['ret'] = 'danger'
                ret['msg'] = '삭제에 실패하였습니다.'
        elif command == 'job_fore_execute':
            db_item = ModelCommand.get_by_id(arg1)
            cmd = (db_item.command + ' ' + db_item.args).strip()
            self.__foreground_execute(f"Command ID: {db_item.id}", shlex.split(cmd), db_item.id)
        elif command == 'job_back_execute':
            self.execute_thread_start(arg1)
            ret['msg'] = "실행 요청을 하였습니다.<br>로그를 확인하세요."
        elif command == 'job_log':
            ret['filename'] = f"command_{arg1}.log"
            if os.path.exists(os.path.join(F.config['path_data'], 'log', f"command_{arg1}.log")) == False:
                ret['ret'] = 'danger'
                ret['msg'] = "로그 파일이 없습니다."
        elif command == 'task_sched':
            job_id = arg1
            flag = (arg2 == 'true')
            scheduler_id = f'command_{job_id}'
            if flag and F.scheduler.is_include(scheduler_id):
                ret['msg'] = '이미 스케쥴러에 등록되어 있습니다.'
            elif flag and F.scheduler.is_include(scheduler_id) == False:
                result = self.__sched_add(job_id)
                ret['msg'] = '스케쥴러에 추가하였습니다.'
            elif flag == False and scheduler.is_include(scheduler_id):
                result = scheduler.remove_job(scheduler_id)
                ret['msg'] = '스케쥴링 취소'
            elif flag == False and scheduler.is_include(scheduler_id) == False:
                ret['msg'] = '등록되어 있지 않습니다.'
        elif command == 'job_process_stop':
            process_ins = SupportSubprocess.get_instance_by_call_id(f"command_{arg1}")
            if process_ins == None:
                ret['msg'] = "실행중인 Process가 없습니다."
            else:
                process_ins.process_close()
                ret['msg'] = "Process를 중지하였습니다."
        return jsonify(ret)

    
    def __foreground_execute(self, title, command, job_id=None):
        
        if command[0] != 'LOAD':
            ToolModalCommand.start(title, [command])
        else:
            F.socketio.emit("command_modal_show", title, namespace='/framework')
            def start_communicate_load(load_log_list):
                def func():
                    while True:
                        logs = load_log_list.getvalue()
                        load_log_list.truncate(0)
                        if logs:
                            P.logger.error(logs)
                            F.socketio.emit("command_modal_add_text", logs.strip() + '\n', namespace='/framework')
                            if logs == '<<END>>':
                                break
                        time.sleep(0.3)
                th = threading.Thread(target=func)
                th.setDaemon(True)
                th.start()

            def func():
                import io
                from contextlib import redirect_stdout
                load_log_list = io.StringIO()
                with redirect_stdout(load_log_list):
                    start_communicate_load(load_log_list)
                    if job_id is not None:
                        command_logger = get_logger(f'command_{job_id}')
                    else:
                        command_logger = P.logger
                    self.__module_load(command, logger=command_logger)
                load_log_list.write("<<END>>")
                load_log_list.flush()
            th = threading.Thread(target=func, args=())
            th.setDaemon(True)
            th.start()
            return 'success'


    def __module_load(self, command, **kwargs):
        try:
            python_filename = command[1]
            python_sys_path = os.path.dirname(python_filename)
            if python_sys_path not in sys.path:
                sys.path.append(python_sys_path)
            module_name = os.path.basename(python_filename).split('.py')[0]
            if module_name not in sys.path:
                sys.path.append(module_name)
            import importlib
            mod = importlib.import_module(module_name)
            importlib.reload(mod)
            args = command
            mod_command_load = getattr(mod, 'main')
            if mod_command_load:
                ret = mod_command_load(*args, **kwargs)
            return ret
        except Exception as e: 
            P.logger.error(f'Exception:{str(e)}')
            P.logger.error(traceback.format_exc())   



    def execute_thread_start(self, job_id):
        th = threading.Thread(target=self.execute_thread_function_by_job_id, args=(job_id,))
        th.setDaemon(True)
        th.start()
        return th


    def execute_thread_function_by_job_id(self, *args, **kwargs):
        #P.logger.error(d(args))
        #P.logger.error(d(kwargs))
        db_item = ModelCommand.get_by_id(args[0])
        kwargs['id'] = args[0]
        self.execute_thread_function((db_item.command + ' ' + db_item.args).strip(), **kwargs)

    
    def execute_thread_function(self, command, **kwargs):
        try:
            cmd = shlex.split(command)
            
            if cmd[0] == 'LOAD':
                command_logger = F.get_logger(f"command_{kwargs['id']}")
                kwargs['logger'] = command_logger
                return self.__module_load(cmd, **kwargs)
            else:
                class LogReceiver:
                    def __init__(self, logger):
                        self.logger = logger

                    def stdout_callback(self, call_id, mode, text):
                        if mode == 'LOG':
                            self.logger.debug(text)
                        else:
                            self.logger.debug(mode)
                command_logger = F.get_logger(f"command_{kwargs['id']}", from_command=True)
                receiver = LogReceiver(command_logger)
                process = SupportSubprocess(cmd, stdout_callback=receiver.stdout_callback, call_id=f"command_{kwargs['id']}")
                process.start()
        except Exception as e: 
            P.logger.error(f'Exception:{str(e)}')
            P.logger.error(traceback.format_exc())        


    def plugin_load(self):
        def plugin_load_thread():
            try:
                db_items = ModelCommand.get_list()
                for db_item in db_items:
                    if db_item.schedule_mode == 'startup':
                        self.execute_thread_start(db_item.id)
                    elif db_item.schedule_mode == 'scheduler' and db_item.schedule_auto_start:
                        self.__sched_add(db_item.id, db_item=db_item)
            except Exception as e: 
                logger.error(f"Exception:{str(e)}")
                logger.error(traceback.format_exc())        
        try:
            th = threading.Thread(target=plugin_load_thread)
            th.setDaemon(True)
            th.start()
        except Exception as e: 
            P.logger.error(f'Exception:{str(e)}')
            P.logger.error(traceback.format_exc())   
    
    
    def __sched_add(self, id, db_item=None):
        try:
            if db_item is None:
                db_item = ModelCommand.get_by_id(id)
            job_id = f"command_{db_item.id}"
            if scheduler.is_include(job_id):
                return
            job = Job(self.P.package_name, job_id, db_item.schedule_interval, self.execute_thread_function_by_job_id, db_item.description,  args=(db_item.id,))
            scheduler.add_job_instance(job)
            return True
        except Exception as e: 
            P.logger.error(f'Exception:{str(e)}')
            P.logger.error(traceback.format_exc())   
        return False










class ModelCommand(ModelBase):
    __tablename__ = 'command_job'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}
    __bind_key__ = 'system'

    id = db.Column(db.Integer, primary_key=True)
    command = db.Column(db.String)
    filepath = db.Column(db.String)
    args = db.Column(db.String)
    description = db.Column(db.String)
    schedule_mode = db.Column(db.String) # none, startup, scheduler
    schedule_auto_start = db.Column(db.Boolean)  # 시작시 스케쥴링 등록
    schedule_interval = db.Column(db.String)  # 주기
    

    def __init__(self, command):
        self.args = ''
        self.description = ''
        self.schedule_mode = 'none'
        self.schedule_auto_start = False
        self.schedule_interval = ''
        self.set_command(command)

    def set_command(self, command):
        self.command = command
        tmp = command.split(' ')
        for t in tmp:
            for ext in ['.py', '.sh', '.bat']:
                if t.endswith(ext):
                    self.filepath = t
                    break


    @classmethod
    def job_new(cls, command):
        item = ModelCommand(command)
        return item.save()


    @classmethod
    def job_list(cls):
        try:
            data = cls.get_list(by_dict=True)
            for item in data:
                item['scheduler_is_include'] = F.scheduler.is_include(f"command_{item['id']}")
                item['scheduler_is_running'] = F.scheduler.is_running(f"command_{item['id']}")

                item['process'] = (SupportSubprocess.get_instance_by_call_id(f"command_{item['id']}") != None)

            return data
        except Exception as e:
            logger.error(f"Exception:{str(e)}")
            logger.error(traceback.format_exc())
