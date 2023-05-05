import os
import threading
import time
import traceback

from flask import request
from framework import F
from support import SingletonClass

namespace = 'log'

@F.socketio.on('connect', namespace='/%s' % namespace)
def socket_connect(): 
    F.logger.debug('log connect')

@F.socketio.on('start', namespace='/%s' % namespace)
def socket_file(data):
    try:
        package = filename = None
        if 'package' in data:
            package = data['package']
        else:
            filename = data['filename']
        LogViewer.instance().start(package, filename, request.sid)
        F.logger.debug('start package:%s filename:%s sid:%s', package, filename, request.sid)
    except Exception as e: 
        F.logger.error(f"Exception:{str(e)}")
        F.logger.error(traceback.format_exc())

@F.socketio.on('disconnect', namespace='/%s' % namespace)
def disconnect():
    try:
        LogViewer.instance().disconnect(request.sid)
        F.logger.debug('disconnect sid:%s', request.sid)
    except Exception as e: 
        F.logger.error(f"Exception:{str(e)}")
        F.logger.error(traceback.format_exc())



class WatchThread(threading.Thread):

    def __init__(self, package, filename):
        super(WatchThread, self).__init__()
        self.stop_flag = False
        self.package = package
        self.filename = filename
        self.daemon = True

    def stop(self):
        self.stop_flag = True

    def run(self):
        F.logger.debug('WatchThread.. Start %s', self.package)
        if self.package is not None:
            logfile = os.path.join(F.config['path_data'], 'log', f'{self.package}.log')
            key = 'package'
            value = self.package
        else:
            logfile = os.path.join(F.config['path_data'], 'log', self.filename)
            key = 'filename'
            value = self.filename
        if os.path.exists(logfile):
            with open(logfile, 'r', encoding='utf8') as f:
                f.seek(0, os.SEEK_END)
                while not self.stop_flag:
                    line = f.readline()
                    if not line:
                        time.sleep(0.1) # Sleep briefly
                        continue
                    F.socketio.emit("add", {key : value, 'data': line}, namespace='/log')
            F.logger.debug('WatchThread.. End %s', value)
        else:
            F.socketio.emit("add", {key : value, 'data': 'not exist logfile'}, namespace='/log')


class LogViewer(SingletonClass):
           
    watch_list = {} 

    @classmethod
    def start(cls, package, filename, sid):
        # 2019-04-02 간만에 봤더니 헷깔려서 적는다
        # 이 쓰레드는 오픈시 이전 데이타만을 보내는 쓰레드다. 실시간보는거 아님.
        
        def thread_function():
            if package is not None:
                logfile = os.path.join(F.config['path_data'], 'log', f'{package}.log')
            else:
                logfile = os.path.join(F.config['path_data'], 'log', filename)
            if os.path.exists(logfile):
                ins_file = open(logfile, 'r', encoding='utf8')  ## 3)
                line = ins_file.read()
                F.socketio.emit("on_start", {'data': line}, namespace='/log')
                F.logger.debug('on_start end')
            else:
                F.socketio.emit("on_start", {'data': 'not exist logfile'}, namespace='/log')
        
        if package is not None:
            key = package
        else:
            key = filename
        thread = threading.Thread(target=thread_function, args=())
        thread.daemon = True
        thread.start()
      

        if key not in cls.watch_list:
            cls.watch_list[key] = {}
            cls.watch_list[key]['sid'] = []
            cls.watch_list[key]['thread'] = WatchThread(package, filename)
            cls.watch_list[key]['thread'].start()
        cls.watch_list[key]['sid'].append(sid)

    @classmethod
    def disconnect(cls, sid):
        find = False
        find_key = None
        for key, value in cls.watch_list.items():
            F.logger.debug('key:%s value:%s', key, value)
            for s in value['sid']:
                if sid == s:
                    find = True
                    find_key = key
                    value['sid'].remove(s)
                    break
            if find:
                break
        if not find:
            return
        if not cls.watch_list[find_key]['sid']:
            F.logger.debug('thread kill')
            cls.watch_list[find_key]['thread'].stop()
            del cls.watch_list[find_key]

