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
                    except Exception:
                        logger.exception(command)
            
            result = []
            thread = threading.Thread(target=func, args=(result,))
            thread.setDaemon(True)
            thread.start()
            #thread.join()

            try:
                #process.communicate()
                process_ret = process.wait(timeout=timeout) # wait for the subprocess to exit
            except Exception:
                logger.exception(command)
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
                except Exception:
                    logger.exception(command)
                    ret2 = ret

            new_ret['log'] = ret2
            return new_ret
        except Exception as e: 
            logger.error(f"Exception:{str(e)}")
            logger.error(traceback.format_exc())
            logger.error('command : %s', command)
        finally:
            try:
                if process.stdout:
                    process.stdout.close()
                if process.stdin:
                    process.stdin.close()
                if process.stderr:
                    process.stderr.close()
            except Exception as e:
                pass

    

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
                else:
                    self.process.wait()
            logger.info(f"{self.command} END")
        except Exception as e: 
            logger.error(f'Exception:{str(e)}')
            logger.error(traceback.format_exc())
            logger.warning(self.command)
            self.send_stdout_callback(self.call_id, 'ERROR', str(e))
            self.send_stdout_callback(self.call_id, 'ERROR', str(traceback.format_exc()))
            self.process_close()
        finally:
            if self.stdout_callback != None:
                #self.stdout_callback(self.call_id, 'thread_end', None)
                pass
            self.remove_instance(self)
            self.process = None

    def __close_pipes(self):
        if self.process is not None:
            logger.debug(f"Close pipes of the process: {self.command}")
            try:
                if self.process.stdin: self.process.stdin.close()
            except Exception: pass
            try:
                if self.process.stdout: self.process.stdout.close()
            except Exception: pass
            try:
                if self.process.stderr: self.process.stderr.close()
            except Exception: pass

    def __start_communicate(self):
        self.stdout_queue = queue.Queue()
        sout = io.open(self.process.stdout.fileno(), 'rb', closefd=False)
       
        def Pump(stream):
            _queue = queue.Queue()
            
            def rdr():
                while True:
                    if self.process is None or self.process.stdout is None:
                        break
                    try:
                        buf = self.process.stdout.read(1)
                    except Exception:
                        logger.exception(self.command)
                        continue
                    #print(buf)
                    if buf:
                        _queue.put( buf )
                    else: 
                        _queue.put( None )
                        break
                _queue.put( None )
                '''
                2025.12.07. halfaider

                communicate() 혹은 with 문을 사용하지 않을 경우 파이프를 명시적으로 닫아줘야 함
                __execute_thread_function()에서 파이프를 닫아버리면 남은 버퍼를 처리하느라 여기서 오류가 발생할 수 있음
                그래서 파이프는 소비하는 이곳에서 닫는 걸로...
                '''
                self.__close_pipes()
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
                    except queue.Empty:
                        pass
                    except Exception:
                        logger.exception(self.command)
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
        if self.process is None:
            return
        try:
            #self.process.terminate()
            #self.process.wait(self.timeout or 5)
            # terminate()하면 재시작시 기존과 다르게 동작, 일관성 위해 기존처럼 kill()
            self.process.kill()
        except Exception:
            try:
                self.process.kill()
                self.process.wait(self.timeout or 5)
            except Exception:
                logger.exception(f"Failed to kill process: {self.command}")
        finally:
            #self.stdout_queue = None
            self.remove_instance(self)
            self.process = None

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
