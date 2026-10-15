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
        finally:
            try:
                if process.stdout:
                    process.stdout.close()
                if process.stdin:
                    process.stdin.close()
            except Exception as e:
                pass

    

    __instance_list = []
    __instance_lock = threading.RLock()


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
        self.__output_threads = []
        self.__callback_thread = None
        self.__output_error = None
        self.__process_lock = threading.Lock()
        self.__stop_requested = False
        

    def start(self, join=True):
        try:
            # Register before spawning so stop-all also includes starting jobs.
            with self.__instance_lock:
                self.__instance_list.append(self)
            self.thread = threading.Thread(target=self.__execute_thread_function, args=())
            self.thread.setDaemon(True)
            self.thread.start()
            if join:
                self.thread.join()
        except Exception as e: 
            logger.error(f'Exception:{str(e)}')
            logger.error(traceback.format_exc())
            self.remove_instance(self)
            self.send_stdout_callback(self.call_id, 'ERROR', traceback.format_exc())


    def __execute_thread_function(self):
        process = None
        error = None
        try:
            self.command = self.command_for_windows(self.command)
            logger.debug(f"{self.command=}")
            preexec = (demote(self.uid, self.gid)
                       if platform.system() != 'Windows' and self.uid is not None
                       else None)
            process = subprocess.Popen(
                self.command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, universal_newlines=True,
                shell=self.shell, env=self.env, encoding='utf8', bufsize=0,
                preexec_fn=preexec)
            with self.__process_lock:
                self.process = process
                stop_requested = self.__stop_requested
            if stop_requested:
                self.process_close()
            self.send_stdout_callback(self.call_id, 'START', None)
            self.__start_communicate()
            self.__start_send_callback()
            process.wait(timeout=self.timeout)
            logger.info(f"{self.command} END")
        except Exception:
            error = traceback.format_exc()
            logger.error(error)
            logger.warning(self.command)
        finally:
            try:
                if process is not None:
                    if process.poll() is None:
                        self.process_close()
                    process.wait()
                    # Do not close pipes or clear the process while buffered
                    # output is still being consumed.
                    for thread in self.__output_threads:
                        if thread.ident is not None:
                            thread.join()
            except Exception:
                error = error or traceback.format_exc()
                logger.error(traceback.format_exc())
            finally:
                self.__close_pipes(process)
                if (self.__callback_thread is not None
                        and self.__callback_thread.ident is not None):
                    self.__callback_thread.join()
                try:
                    error = error or self.__output_error
                    if error is not None:
                        self.send_stdout_callback(self.call_id, 'ERROR', error)
                    elif process is not None:
                        self.send_stdout_callback(self.call_id, 'END', None)
                finally:
                    self.remove_instance(self)
                    with self.__process_lock:
                        self.process = None

    def __close_pipes(self, process):
        if process is not None:
            for stream in (process.stdin, process.stdout, process.stderr):
                if stream is not None:
                    try:
                        stream.close()
                    except Exception:
                        logger.error(traceback.format_exc())

    def __start_communicate(self):
        self.stdout_queue = stdout_queue = queue.Queue()
        process = self.process
        assert process is not None and process.stdout is not None
        stdout = process.stdout
        output = queue.Queue()

        def rdr():
            try:
                for buf in iter(lambda: stdout.read(1), ''):
                    output.put(buf)
            except Exception:
                self.__output_error = traceback.format_exc()
                logger.error(self.__output_error)
                self.process_close()
            finally:
                output.put(None)

        def clct():
            active = True
            while active:
                chunk = output.get()
                if chunk is None:
                    break
                try:
                    while True:
                        following = output.get(timeout=0.005)
                        if following is None:
                            active = False
                            break
                        chunk += following
                except queue.Empty:
                    pass
                stdout_queue.put(chunk)
            stdout_queue.put('\n')
            stdout_queue.put(None)

        for target in (rdr, clct):
            thread = threading.Thread(target=target)
            thread.daemon = True
            self.__output_threads.append(thread)
            thread.start()

    def __start_send_callback(self):
        stdout_queue = self.stdout_queue
        assert stdout_queue is not None

        def func():
            while True:
                chunk = stdout_queue.get()
                if chunk is None:
                    break
                self.send_stdout_callback(self.call_id, 'LOG', chunk)

        def func_callback_line():
            previous = ''
            while True:
                chunk = stdout_queue.get()
                if chunk is None:
                    break
                receive = previous + chunk
                lines = receive.split('\n')
                previous = lines[-1]
                for line in lines[:-1]:
                    line = line.strip()
                    self.send_stdout_callback(self.call_id, 'LOG', line)

        target = func_callback_line if self.callback_line else func
        self.__callback_thread = threading.Thread(target=target)
        self.__callback_thread.daemon = True
        self.__callback_thread.start()

    def process_close(self):
        with self.__process_lock:
            self.__stop_requested = True
            process = self.process
        try:
            if process is not None and process.poll() is None:
                process.kill()
        except Exception:
            logger.error(traceback.format_exc())
        # The execution worker reaps the child, drains output, and closes pipes.

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
        # Stop the current snapshot; jobs started after it remain independent.
        for instance in cls.get_list():
            instance.process_close()


    @classmethod
    def remove_instance(cls, remove_instance):
        with cls.__instance_lock:
            cls.__instance_list[:] = [instance for instance in cls.__instance_list
                                      if instance is not remove_instance]
    
    @classmethod
    def print(cls):
        for instance in cls.get_list():
            logger.info(instance.command)


    @classmethod
    def get_instance_by_call_id(cls, call_id):
        for instance in cls.get_list():
            if instance.call_id == call_id:
                return instance
    
    @classmethod
    def get_list(cls):
        with cls.__instance_lock:
            return list(cls.__instance_list)
