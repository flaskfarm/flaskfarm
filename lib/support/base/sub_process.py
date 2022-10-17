import io
import json
import os
import platform
import queue
import subprocess
import threading
import time
import traceback

from . import logger


def demote(user_uid, user_gid):
    def result():
        os.setgid(user_gid)
        os.setuid(user_uid)
    return result

class SupportSubprocess(object):

    # 2021-10-25
    # timeout 적용
    @classmethod
    def execute_command_return(cls, command, format=None, log=False, shell=False, env=None, timeout=None, uid=None, gid=None):

        try:
            logger.debug(f"execute_command_return : {' '.join(command)}")
            if platform.system() == 'Windows':
                tmp = []
                if type(command) == type([]):
                    for x in command:
                        if x.find(' ') == -1:
                            tmp.append(x)
                        else:
                            tmp.append(f'"{x}"')
                    command = ' '.join(tmp)

            iter_arg =  ''
            if platform.system() == 'Windows':
                process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, shell=shell, env=env, encoding='utf8')
            else:
                if uid == None:
                    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, shell=shell, env=env, encoding='utf8')
                else:
                    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, shell=shell, env=env, preexec_fn=demote(uid, gid), encoding='utf8')
                
                

            new_ret = {'status':'finish', 'log':None}
            try:
                process_ret = process.wait(timeout=timeout) # wait for the subprocess to exit
            except:
                import psutil
                process = psutil.Process(process.pid)
                for proc in process.children(recursive=True):
                    proc.kill()
                process.kill()
                new_ret['status'] = "timeout"

            ret = []
            with process.stdout:
                for line in iter(process.stdout.readline, iter_arg):
                    ret.append(line.strip())
                    if log:
                        logger.debug(ret[-1])

            if format is None:
                ret2 = '\n'.join(ret)
            elif format == 'json':
                try:
                    index = 0
                    for idx, tmp in enumerate(ret):
                        #logger.debug(tmp)
                        if tmp.startswith('{') or tmp.startswith('['):
                            index = idx
                            break
                    ret2 = json.loads(''.join(ret[index:]))
                except:
                    ret2 = None

            new_ret['log'] = ret2
            return new_ret
        except Exception as exception: 
            logger.error('Exception:%s', exception)
            logger.error(traceback.format_exc())
            logger.error('command : %s', command)
    

    instance_list = []


    def __init__(self, command,  print_log=False, shell=False, env=None, timeout=None, uid=None, gid=None, stdout_callback=None):
        self.command = command
        self.print_log = print_log
        self.shell = shell
        self.env = env
        self.timeout = timeout
        self.uid = uid
        self.gid = gid
        self.stdout_callback = stdout_callback
        self.process = None
        self.stdout_queue = None
        

    def start(self, join=True):
        try:
            self.thread = threading.Thread(target=self.execute_thread_function, args=())
            self.thread.setDaemon(True)
            self.thread.start()
            if join:
                self.thread.join()
        except Exception as e: 
            logger.error(f'Exception:{str(e)}')
            logger.error(traceback.format_exc())


    def execute_thread_function(self):
        try:
            if platform.system() == 'Windows':
                tmp = []
                if type(self.command) == type([]):
                    for x in self.command:
                        if x.find(' ') == -1:
                            tmp.append(x)
                        else:
                            tmp.append(f'"{x}"')
                    self.command = ' '.join(tmp)

            if platform.system() == 'Windows':
                self.process = subprocess.Popen(self.command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, shell=self.shell, env=self.env, encoding='utf8')
            else:
                if self.uid == None:
                    self.process = subprocess.Popen(self.command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, shell=self.shell, env=self.env, encoding='utf8')
                else:
                    self.process = subprocess.Popen(self.command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, shell=self.shell, env=self.env, preexec_fn=demote(self.uid, self.gid), encoding='utf8')
            SupportSubprocess.instance_list.append(self)
            self.start_communicate()
            self.start_send_callback()
            if self.process is not None:
                self.process.wait()
            logger.info(f"{self.command} END")
        except Exception as e: 
            logger.error(f'Exception:{str(e)}')
            logger.error(traceback.format_exc())
            if self.stdout_callback != None:
                self.stdout_callback('error', str(e))
                self.stdout_callback('error', str(traceback.format_exc()))
        finally:
            if self.stdout_callback != None:
                self.stdout_callback('thread_end', None)
    

    def start_communicate(self):
        self.stdout_queue = queue.Queue()
        sout = io.open(self.process.stdout.fileno(), 'rb', closefd=False)
       
        def Pump(stream):
            _queue = queue.Queue()
            
            def rdr():
                while True:
                    buf = self.process.stdout.read(1)
                    if buf:
                        _queue.put( buf )
                    else: 
                        _queue.put( None )
                        break
                _queue.put( None )
                time.sleep(1)

            def clct():
                active = True
                while active:
                    r = _queue.get()
                    if r is None:
                        break
                    try:
                        while True:
                            r1 = _queue.get(timeout=0.005)
                            if r1 is None:
                                active = False
                                break
                            else:
                                r += r1
                    except:
                        pass
                    if r is not None:
                        #print(f"{r=}")
                        self.stdout_queue.put(r)
                self.stdout_queue.put('<END>')
            for tgt in [rdr, clct]:
                th = threading.Thread(target=tgt)
                th.setDaemon(True)
                th.start()
        Pump(sout)


    def start_send_callback(self):
        def func():
            while self.stdout_queue:
                line = self.stdout_queue.get()
                if line == '<END>':
                    if self.stdout_callback != None:
                        self.stdout_callback('end', None)
                    break
                else:
                    if self.stdout_callback != None:
                        self.stdout_callback('log', line)
        th = threading.Thread(target=func, args=())
        th.setDaemon(True)
        th.start()


    def process_close(self):
        try:
            if self.process is not None and self.process.poll() is None:
                #import psutil
                #process = psutil.Process(instance.process.pid)
                #for proc in instance.process.children(recursive=True):
                #    proc.kill()
                self.process.kill()
        except Exception as e: 
            logger.error(f'Exception:{str(e)}')
            logger.error(traceback.format_exc())           
        finally:
            try:
                #self.stdout_queue = None 
                self.process.kill()
            except: pass

    def input_command(self, cmd):
        if self.process != None:
            self.process.stdin.write(f'{cmd}\n')
            self.process.stdin.flush()


    @classmethod
    def all_process_close(cls):
        for instance in cls.instance_list:
            instance.process_close()
        cls.instance_list = []

    