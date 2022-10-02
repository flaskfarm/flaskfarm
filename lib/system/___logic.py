# -*- coding: utf-8 -*-
#########################################################
# python
import os
import traceback
import logging
from datetime import datetime
import string
import random
import json

# third-party
import requests
from flask import Blueprint, request, Response, send_file, render_template, redirect, jsonify
from flask_login import login_user, logout_user, current_user, login_required


from framework import F, frame, app, db, scheduler, VERSION, path_app_root, logger, Job, User
from framework.util import Util

# 패키지
from .model import ModelSetting 
import system

#########################################################

class SystemLogic(object):
    point = 0
    db_default = { 
        'db_version' : '1',
        'port' : '9999',
        'ddns' : 'http://localhost:9999',
        #'url_filebrowser' : 'http://localhost:9998',
        #'url_celery_monitoring' : 'http://localhost:9997',
        'id' : 'admin', 
        'pw' : '//nCv0/YkVI3U2AAgYwOuJ2hPlQ7cDYIbuaCt4YJupY=',
        'system_start_time' : '',
        'repeat' : '',
        'auto_restart_hour' : '12',
        #'unique' : '',
        'theme' : 'Cerulean',
        'log_level' : '10',
        'use_login' : 'False',
        'link_json' : '[{"type":"link","title":"위키","url":"https://sjva.me/wiki/public/start"}]', 
        'plugin_dev_path': '',
        'plugin_tving_level2' : 'False', 
        'web_title' : 'Home',
        'my_ip' : '',
        'wavve_guid' : '', 

        #인증
        'auth_use_apikey' : 'False',
        'auth_apikey' : '',
        #'hide_menu' : 'True',

        #Selenium
        'selenium_remote_url' : '',        
        'selenium_remote_default_option' : '--no-sandbox\n--disable-gpu',
        'selenium_binary_default_option' : '',

        # notify
        'notify_telegram_use' : 'False',
        'notify_telegram_token' : '',
        'notify_telegram_chat_id' : '',
        'notify_telegram_disable_notification' : 'False',
        'notify_discord_use' : 'False',
        'notify_discord_webhook' : '',
        
        'notify_advaned_use' : 'False',
        'notify_advaned_policy' : u"# 각 플러그인 설정 설명에 명시되어 있는 ID = 형식\n# DEFAULT 부터 주석(#) 제거 후 작성\n\n# DEFAULT = ",

        # telegram
        'telegram_bot_token' : '',
        'telegram_bot_auto_start' : 'False',
        'telegram_resend' : 'False', 
        'telegram_resend_chat_id' : '', 

        # 홈페이지 연동 2020-06-07
        'sjva_me_user_id' : '',
        'auth_status' : '',
        'sjva_id' : '',
  
        # memo
        'memo' : '',

        # tool - decrypt
        'tool_crypt_use_user_key' : 'False',
        'tool_crypt_user_key' : '',
        'tool_crypt_encrypt_word' : '',
        'tool_crypt_decrypt_word' : '',
        
        'use_beta' : 'False',
    }



    @staticmethod
    def get_info():
        info = {}
        import platform
        info['platform'] = platform.platform()
        info['processor'] = platform.processor()

        import sys
        info['python_version'] = sys.version
        info['version'] = VERSION
        info['recent_version'] = SystemLogic.recent_version
        info['path_app_root'] = path_app_root
        info['running_type'] = u'%s.  비동기 작업 : %s' % (frame.config['running_type'], u"사용" if frame.config['use_celery'] else "미사용")
        import system
        
        info['auth'] = frame.config['member']['auth_desc']
        info['cpu_percent'] = 'not supported'
        info['memory'] = 'not supported'
        info['disk'] = 'not supported'
        if frame.config['running_type'] != 'termux':
            try:
                import psutil
                from framework.util import Util
                info['cpu_percent'] = '%s %%' % psutil.cpu_percent() 
                tmp = psutil.virtual_memory()
                #info['memory'] = [Util.sizeof_fmt(tmp[0], suffix='B'), Util.sizeof_fmt(tmp[3]), Util.sizeof_fmt(tmp[1]), tmp[2]]
                info['memory'] = u'전체 : %s   사용량 : %s   남은량 : %s  (%s%%)' % (Util.sizeof_fmt(tmp[0], suffix='B'), Util.sizeof_fmt(tmp[3], suffix='B'), Util.sizeof_fmt(tmp[1], suffix='B'), tmp[2])
            except:
                pass

            try:
                import platform
                if platform.system() == 'Windows':
                    s = os.path.splitdrive(path_app_root)
                    root = s[0]
                else:
                    root = '/'
                tmp = psutil.disk_usage(root)
                info['disk'] = u'전체 : %s   사용량 : %s   남은량 : %s  (%s%%) - 드라이브 (%s)' % (Util.sizeof_fmt(tmp[0], suffix='B'), Util.sizeof_fmt(tmp[1], suffix='B'), Util.sizeof_fmt(tmp[2], suffix='B'), tmp[3], root)
            except Exception as exception: 
                pass
        try:
            tmp = SystemLogic.get_setting_value('system_start_time')
            #logger.debug('SYSTEM_START_TIME:%s', tmp)
            tmp_datetime = datetime.strptime(tmp, '%Y-%m-%d %H:%M:%S')
            timedelta = datetime.now() - tmp_datetime
            info['time'] = u'시작 : %s   경과 : %s   재시작 : %s' % (tmp, str(timedelta).split('.')[0], frame.config['arg_repeat'])
        except Exception as exception: 
            info['time'] = str(exception)
        return info


    @staticmethod
    def setting_save_system(req):
        try:
            for key, value in req.form.items():
                logger.debug('Key:%s Value:%s', key, value)
                entity = db.session.query(ModelSetting).filter_by(key=key).with_for_update().first()
                entity.value = value
                #if key == 'theme':
                #    SystemLogic.change_theme(value)
            db.session.commit()
            lists = ModelSetting.query.all()
            SystemLogic.setting_list = Util.db_list_to_dict(lists)
            frame.users[db.session.query(ModelSetting).filter_by(key='id').first().value] = User(db.session.query(ModelSetting).filter_by(key='id').first().value, passwd_hash=db.session.query(ModelSetting).filter_by(key='pw').first().value)
            SystemLogic.set_restart_scheduler()
            frame.set_level(int(db.session.query(ModelSetting).filter_by(key='log_level').first().value))
            
            return True                  
        except Exception as exception: 
            logger.error('Exception:%s', exception)
            logger.error(traceback.format_exc())
            return False
    
    @staticmethod
    def setting_save_after():
        try:
            frame.users[ModelSetting.get('id')] = User(ModelSetting.get('id'), passwd_hash=ModelSetting.get('pw'))
            SystemLogic.set_restart_scheduler()
            frame.set_level(int(db.session.query(ModelSetting).filter_by(key='log_level').first().value))
            from .logic_site import SystemLogicSite
            SystemLogicSite.get_daum_cookies(force=True)
            SystemLogicSite.create_tving_instance()
            return True                  
        except Exception as exception: 
            logger.error('Exception:%s', exception)
            logger.error(traceback.format_exc())
            return False
    
    @staticmethod
    def change_theme(theme):
        try:
            source = os.path.join(path_app_root, 'static', 'css', 'theme', '%s_bootstrap.min.css' % theme)
            target = os.path.join(path_app_root, 'static', 'css', 'bootstrap.min.css')
            os.remove(target)
        except Exception as exception: 
            logger.error('Exception:%s', exception)
            logger.error(traceback.format_exc())
            return False
    
    @staticmethod
    def get_setting_value(key):
        try:
            #logger.debug('get_setting_value:%s', key)
            entity = db.session.query(ModelSetting).filter_by(key=key).first()
            if entity is None:
                return None
            else:
                return entity.value
        except Exception as exception: 
            logger.error('Exception:%s', exception)
            logger.error(traceback.format_exc())
            logger.error('error key : %s', key)
            return False
    
    

    
    
    

    @staticmethod
    def command_run(command_text):
        try:
            ret = {}
            tmp = command_text.strip().split(' ')
            if not tmp:
                ret['ret'] = 'success'
                ret['log'] = 'Empty..'
                return ret
            if tmp[0] == 'set':
                if len(tmp) == 3:
                    if tmp[1] == 'token':
                        tmp[1] = 'unique'
                    entity = db.session.query(ModelSetting).filter_by(key=tmp[1]).with_for_update().first()
                    if entity is None:
                        ret['ret'] = 'fail'
                        ret['log'] = '%s not exist' % tmp[1]
                        return ret
                    entity.value = tmp[2] if tmp[2] != 'EMPTY' else ""
                    db.session.commit()
                    ret['ret'] = 'success'
                    ret['log'] = '%s - %s' % (tmp[1], tmp[2])
                    return ret
            
            if tmp[0] == 'set2':
                if tmp[1] == 'klive':
                    from klive import ModelSetting as KLiveModelSetting
                    if KLiveModelSetting.get(tmp[2]) is not None:
                        KLiveModelSetting.set(tmp[2], tmp[3])
                        ret['ret'] = 'success'
                        ret['log'] = f'KLive 설정 값 변경 : {tmp[2]} - {tmp[3]}'
                        return ret
                   
            
            ret['ret'] = 'fail'
            ret['log'] = 'wrong command'
            return ret
        except Exception as exception: 
            logger.error('Exception:%s', exception)
            logger.error(traceback.format_exc())
            ret['ret'] = 'fail'
            ret['log'] = str(exception)
            return ret

    @staticmethod
    def link_save(link_data_str):
        try:
            data = json.loads(link_data_str)
            entity = db.session.query(ModelSetting).filter_by(key='link_json').with_for_update().first()
            entity.value = link_data_str
            db.session.commit()
            SystemLogic.apply_menu_link()
            return True
        except Exception as exception: 
            logger.error('Exception:%s', exception)
            logger.error(traceback.format_exc())
            return False

