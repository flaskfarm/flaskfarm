import io
import json
import locale
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

    @classmethod 
    def command_for_windows(cls, command: list): 
        if platform.system() == 'Windows':
            tmp = []
            if type(command) == type([]):
                for x in command:
                    if x.find(' ') == -1:
                        tmp.append(x)
                    else:
                        tmp.append(f'"{x}"')
                command = ' '.join(tmp)
        return command

    # 2021-10-25
    # timeout 적용
    @classmethod
    def execute_command_return(cls, command, format=None, log=False, shell=False, env=None, timeout=None, uid=None, gid=None):

        try:
            logger.debug(f"execute_command_return : {' '.join(command)}")
            command = cls.command_for_windows(command)

            iter_arg =  ''
            if platform.system() == 'Windows':
                process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, shell=shell, env=env, encoding='utf8', bufsize=0)
            else:
                if uid == None:
                    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, shell=shell, env=env, encoding='utf8')
                else:
                    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, shell=shell, env=env, preexec_fn=demote(uid, gid), encoding='utf8')
            new_ret = {'status':'finish', 'log':None}

            def func(ret):
                with process.stdout:
                    try:
                        for line in iter(process.stdout.readline, iter_arg):
                            ret.append(line.strip())
                            if log:
                                logger.debug(ret[-1])
                    except:
                        pass
            
            result = []
            thread = threading.Thread(target=func, args=(result,))
            thread.setDaemon(True)
            thread.start()
            #thread.join()

            try:
                #process.communicate()
                process_ret = process.wait(timeout=timeout) # wait for the subprocess to exit
            except:
                import psutil
                process = psutil.Process(process.pid)
                for proc in process.children(recursive=True):
                    proc.kill()
                process.kill()
                new_ret['status'] = "timeout"
            #logger.error(process_ret)
            thread.join()
            #ret = []
            #with process.stdout:
            #    for line in iter(process.stdout.readline, iter_arg):
            #        ret.append(line.strip())
            #        if log:
            #            logger.debug(ret[-1])
           
            ret = result
            #logger.error(ret)
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
                    ret2 = ret

            new_ret['log'] = ret2
            return new_ret
        except Exception as e: 
            logger.error(f"Exception:{str(e)}")
            logger.error(traceback.format_exc())
            logger.error('command : %s', command)
    

    __instance_list = []


    def __init__(self, command,  print_log=False, shell=False, env=None, timeout=None, uid=None, gid=None, stdout_callback=None, call_id=None, callback_line=True):
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
        self.call_id = call_id
        self.timestamp = time.time()
        self.callback_line = callback_line
        

    def start(self, join=True):
        try:
            self.thread = threading.Thread(target=self.__execute_thread_function, args=())
            self.thread.setDaemon(True)
            self.thread.start()
            if join:
                self.thread.join()
        except Exception as e: 
            logger.error(f'Exception:{str(e)}')
            logger.error(traceback.format_exc())


    def __execute_thread_function(self):
        try:
            self.command = self.command_for_windows(self.command)
            logger.debug(f"{self.command=}")
            if platform.system() == 'Windows':
                self.process = subprocess.Popen(self.command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, shell=self.shell, env=self.env, encoding='utf8', bufsize=0)

            else:
                if self.uid == None:
                    self.process = subprocess.Popen(self.command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, shell=self.shell, env=self.env, encoding='utf8', bufsize=0)
                else:
                    self.process = subprocess.Popen(self.command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, shell=self.shell, env=self.env, preexec_fn=demote(self.uid, self.gid), encoding='utf8', bufsize=0)
            SupportSubprocess.__instance_list.append(self)
            self.send_stdout_callback(self.call_id, 'START', None)
            self.__start_communicate()
            self.__start_send_callback()
            if self.process is not None:
                if self.timeout != None:
                    self.process.wait(timeout=self.timeout)
                    self.process_close()
                else:
                    self.process.wait()
            self.remove_instance(self)
            logger.info(f"{self.command} END")
        except Exception as e: 
            logger.error(f'Exception:{str(e)}')
            logger.error(traceback.format_exc())
            logger.warning(self.command)
            self.send_stdout_callback(self.call_id, 'ERROR', str(e))
            self.send_stdout_callback(self.call_id, 'ERROR', str(traceback.format_exc()))
        finally:
            if self.stdout_callback != None:
                #self.stdout_callback(self.call_id, 'thread_end', None)
                pass
    

    def __start_communicate(self):
        self.stdout_queue = queue.Queue()
        sout = io.open(self.process.stdout.fileno(), 'rb', closefd=False)
       
        def Pump(stream):
            _queue = queue.Queue()
            
            def rdr():
                while True:
                    try:
                        buf = self.process.stdout.read(1)
                    except:
                        continue
                    #print(buf)
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
                self.stdout_queue.put('\n')
                self.stdout_queue.put('<END>')
                self.stdout_queue.put('\n')
            for tgt in [rdr, clct]:
                th = threading.Thread(target=tgt)
                th.setDaemon(True)
                th.start()
        Pump(sout)


    def __start_send_callback(self):
        def func():
            while self.stdout_queue:
                line = self.stdout_queue.get()
                #logger.error(line)
                if line == '<END>':
                    self.send_stdout_callback(self.call_id, 'END', None)
                    break
                else:
                    self.send_stdout_callback(self.call_id, 'LOG', line)
            self.remove_instance(self)

        def func_callback_line():
            previous = ''
            while self.stdout_queue:
                receive = previous + self.stdout_queue.get()
                lines = receive.split('\n')
                previous = lines[-1]

                for line in lines[:-1]:
                    line = line.strip()
                    # TODO
                    #logger.error(line)
                    if line == '<END>':
                        self.send_stdout_callback(self.call_id, 'END', None)
                        break
                    else:
                        self.send_stdout_callback(self.call_id, 'LOG', line)
            self.remove_instance(self)

        if self.callback_line:
            th = threading.Thread(target=func_callback_line, args=())
        else:
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
        
        self.remove_instance(self)

    def input_command(self, cmd):
        if self.process != None:
            self.process.stdin.write(f'{cmd}\n')
            self.process.stdin.flush()

    def send_stdout_callback(self, call_id, mode, data):
        try:
            if self.stdout_callback != None:
                self.stdout_callback(self.call_id, mode, data)
        except Exception as e: 
            logger.error(f'Exception:{str(e)}')
            logger.error(f"[{call_id}] [{mode}] [{data}]")
            #logger.error(traceback.format_exc())   


    @classmethod
    def all_process_close(cls):
        for instance in cls.__instance_list:
            instance.process_close()
        cls.__instance_list = []


    @classmethod
    def remove_instance(cls, remove_instance):
        new = []
        for instance in cls.__instance_list:
            if remove_instance.timestamp == instance.timestamp:
                continue
            new.append(instance)
        cls.__instance_list = new
    
    @classmethod
    def print(cls):
        for instance in cls.__instance_list:
            logger.info(instance.command)


    @classmethod
    def get_instance_by_call_id(cls, call_id):
        for instance in cls.__instance_list:
            if instance.call_id == call_id:
                return instance
    
    @classmethod
    def get_list(cls):
        return cls.__instance_list
