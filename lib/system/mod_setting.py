import random
import string
import time

from support import (SupportDiscord, SupportFile, SupportSubprocess,
                     SupportTelegram, SupportYaml, SupportSlack)
from tool import ToolModalCommand

from .setup import *

name = 'setting'

class ModuleSetting(PluginModuleBase):
    db_default = {
        'db_version' : '1.1',
        'port' : '9999',
        'ddns' : 'http://localhost:9999',
        'use_login' : 'False',
        'web_id': 'admin',
        'web_pw': '21232f297a57a5a743894a0e4a801fc3',
        'web_title': 'Home',
        'use_apikey': 'False',
        'apikey': ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10)),
        'app_id': ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10)),
        f'restart_interval': f'{random.randint(0,59)} {random.randint(1,23)} * * *',
        'restart_notify': 'False',
        'theme' : 'Cerulean',
        'log_level' : '20',
        'system_start_time': '',
        # notify
        'notify_telegram_use' : 'False',
        'notify_telegram_token' : '',
        'notify_telegram_chat_id' : '',
        'notify_telegram_disable_notification' : 'False',
        'notify_discord_use' : 'False',
        'notify_discord_webhook' : '',
        'notify_slack_use' : 'False',
        'notify_slack_webhook' : '',
        'notify_advaned_use' : 'False',
        'notify.yaml': '', #직접 사용하지 않으나 저장 편의상.
        'command_text': '',
        'celery_start_by_web': 'True', #if F.config['running_type'] == 'docker_alpine' else 'False', #웹 실행시 celery 실행
        'celery_start_command': f"celery -A flaskfarm.main.celery worker --loglevel=info --pool=gevent --concurrency=2 --config_filepath={F.config['config_filepath']} --running_type={F.config['running_type']}",
        

    } 

    def __init__(self, P):
        super(ModuleSetting, self).__init__(P, name=name, first_menu='basic')
        

    def process_menu(self, page, req):
        arg = P.ModelSetting.to_dict()
        try:
            if page == 'config':
                arg['config.yaml'] = SupportFile.read_file(F.config['config_filepath'])
                arg['config_filepath'] = F.config['config_filepath']
            elif page == 'export':
                arg['export_filepath'] = F.config['export_filepath']
                if F.config['exist_export']:
                    arg['export.sh'] = SupportFile.read_file(export)
                else:
                    arg['export.sh'] = "export.sh 파일이 없습니다."
            elif page == 'menu':
                arg['menu_yaml_filepath'] = F.config['menu_yaml_filepath']
                arg['menu.yaml'] = SupportFile.read_file(arg['menu_yaml_filepath'])
            elif page == 'notify':
                arg['notify_yaml_filepath'] = F.config['notify_yaml_filepath']
                arg['notify.yaml'] = SupportFile.read_file(arg['notify_yaml_filepath'])
            elif page == 'celery':
                arg['use_celery'] = F.config['use_celery']
                arg['running_type'] = F.config['running_type']
            return render_template(f'{__package__}_{name}_{page}.html', arg=arg)
        except Exception as e: 
            P.logger.error(f'Exception:{str(e)}')
            P.logger.error(traceback.format_exc())
            return render_template('sample.html', title=f"{__package__}/{name}/{page}")


    def process_command(self, command, arg1, arg2, arg3, req):
        ret = {'ret':'success'}
        if command == 'apikey_generate':
            return jsonify(''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10)))
        elif command == 'config_save':
            SupportFile.write_file(F.config['config_filepath'], arg1 )
            ret['msg'] = '저장하였습니다.'
        elif command == 'export_save':
            if F.config['exist_export']:
                SupportFile.write_file(F.config['export_filepath'], arg1 )
                ret['msg'] = '저장하였습니다.'
            else:
                ret['ret'] = 'warning'
                ret['msg'] = 'export.sh 파일이 없습니다.'
        elif command == 'menu_save':
            SupportFile.write_file(F.config['menu_yaml_filepath'], arg1 )
            try:
                SupportYaml.read_yaml(F.config['menu_yaml_filepath'])
                ret['msg'] = '저장하였습니다.'
                from framework.init_menu import MenuManager
                MenuManager.init_menu()
                F.socketio.emit("refresh", {}, namespace='/framework')
            except:
                ret['ret'] = "danger" 
                ret['msg'] = "yaml 형식에 맞지 않습니다"
        elif command == 'notify_test':
            if arg1 == 'telegram':
                token, chatid, sound, text = arg2.split('||')
                sound = True if sound == 'true' else False
                SupportTelegram.send_telegram_message(text, image_url=None, bot_token=token, chat_id=chatid, disable_notification=sound)
                ret['msg'] = '메시지를 전송했습니다.'
            elif arg1 == 'discord':
                SupportDiscord.send_discord_message(arg3, webhook_url=arg2)
                ret['msg'] = '메시지를 전송했습니다.'
            elif arg1 == 'slack':
                SupportSlack.send_slack_message(arg3, webhook_url=arg2)
                ret['msg'] = '메시지를 전송했습니다.'
            elif arg1 == 'advanced':
                from tool import ToolNotify
                ToolNotify.send_advanced_message(arg3, message_id=arg2)
                ret['msg'] = '메시지를 전송했습니다.'
        elif command == 'ddns_test':
            try:
                import requests
                url = arg1 + '/version'
                res = requests.get(url)
                data = res.text
                ret['msg'] = f"버전: {data}"
            except Exception as e: 
                P.logger.error(f'Exception:{str(e)}')
                P.logger.error(traceback.format_exc())
                ret['msg'] = str(e)
                ret['type'] = 'warning'
        elif command == 'command_run':
            ret['msg'] = arg1
            pass
        elif command == 'celery_execute':
            self.celery_execute(arg1, mode='foreground')
        elif command == 'celery_execute_back':
            self.celery_execute(arg1, mode='background')
            ret['msg'] = '실행했습니다.'
        elif command == 'celery_test':
            return self.__celery_test()
  
        return jsonify(ret)


    def plugin_load(self):
        try:
            if F.config['run_flask'] == False:
                return

            if F.config['arg_repeat'] == 0 or SystemModelSetting.get('system_start_time') == '':
                SystemModelSetting.set('system_start_time', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            SystemModelSetting.set('repeat', str(F.config['arg_repeat']))
            username = SystemModelSetting.get('web_id')
            passwd = SystemModelSetting.get('web_pw')
            F.users[username] = User(username, passwd_hash=passwd)

            self.__set_restart_scheduler()
            self.__set_scheduler_check_scheduler()
            F.get_recent_version()

            notify_yaml_filepath = os.path.join(F.config['path_data'], 'db', 'notify.yaml')
            if os.path.exists(notify_yaml_filepath) == False:
                import shutil
                shutil.copy(
                    os.path.join(F.config['path_app'], 'files', 'notify.yaml.template'),
                    notify_yaml_filepath
                )
            if SystemModelSetting.get_bool('restart_notify'):
                from tool import ToolNotify
                msg = f"시스템이 시작되었습니다.\n재시작: {F.config['arg_repeat']}"
                ToolNotify.send_message(msg, message_id='system_start')
            if SystemModelSetting.get_bool('celery_start_by_web'):
                # 2022-11-14 DB는 flask가 만드는데 만들기전 celery를 실행해버림
                from threading import Timer
                Timer(10, self.celery_execute).start()
                #self.celery_execute()            

        except Exception as e:
            P.logger.error(f'Exception:{str(e)}')
            P.logger.error(traceback.format_exc())

    def plugin_unload(self):
        ToolModalCommand.modal_close()

    def setting_save_after(self, change_list):
        if 'theme' in change_list or 'web_title' in change_list:
            F.socketio.emit("refresh", {}, namespace='/framework')
        elif 'notify.yaml' in change_list:
            try:
                SupportFile.write_file(F.config['notify_yaml_filepath'], SystemModelSetting.get('notify.yaml'))
                SupportYaml.read_yaml(F.config['notify_yaml_filepath'])
            except:
                data = {'type':'danger', 'msg' : "알림 정책이 yaml 형식에 맞지 않습니다."}
                F.socketio.emit("notify", data, namespace='/framework')
        elif 'web_pw' in change_list:
            import hashlib
            enc = hashlib.md5()
            enc.update(SystemModelSetting.get('web_pw').encode())
            SystemModelSetting.set('web_pw', enc.hexdigest())
        elif 'restart_interval' in change_list:
            if SystemModelSetting.get('restart_interval') == '':
                SystemModelSetting.set('restart_interval', '0')
            self.__set_restart_scheduler()
        elif 'log_level' in change_list:
            F.set_level(SystemModelSetting.get_int('log_level'))



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


    def celery_execute(self, command=None, mode='background'):
        if command == None:
            command = SystemModelSetting.get('celery_start_command')
        command = command.replace("{F.config['config_filepath']}", F.config['config_filepath']).replace('{F.config["config_filepath"]}', F.config['config_filepath']).replace("{F.config['path_working']}", F.config['path_working']).replace('{F.config["path_working"]}', F.config['path_working'])
        command = command.split(' ')
        if mode == 'foreground':
            cmd = [
                ['msg', f"명령 : {' '.join(command)}"],
                command,
            ]
            ToolModalCommand.start("Celery 실행", cmd)
        elif mode == 'background':
            SupportSubprocess(command).start(join=False)


    def __celery_test(self):
        if F.config['use_celery']:
            from celery import Celery
            from celery.exceptions import NotRegistered, TimeoutError
            data = {}
            try:
                result = self.celery_test.apply_async()
                try:
                    tmp = result.get(timeout=5, propagate=True)
                except Exception as e:
                    P.logger.error(f'Exception:{str(e)}')
                    P.logger.error(traceback.format_exc())
                data['ret'] = 'success'
                data['msg'] = tmp
            except TimeoutError:
                data['ret'] = 'danger'
                data['msg'] = 'celery가 동작중이 아니거나 모든 Worker가 작업중입니다.'
            except NotRegistered:
                data['ret'] = 'danger'
                data['msg'] = 'Not Registered'
            except:
                data['ret'] = 'danger'
                data['msg'] = '실패'
        else:
            data['ret'] = 'danger'
            data['msg'] = 'celery 실행환경이 아닙니다.'
        P.logger.debug(d(data))
        return data

    #@staticmethod
    @celery.task
    def celery_test():
        try:
            time.sleep(1)
            data = '정상입니다. 이 메시지는 celery 에서 반환됩니다. '
            return data
        except Exception as e:
            P.logger.error(f'Exception:{str(e)}')
            P.logger.error(traceback.format_exc())
