import enum
import os
import platform
import re
import shutil
import subprocess
import threading
import time
import traceback
from datetime import datetime

from support import SupportFile, SupportSubprocess, SupportUtil, logger


class SupportFfmpeg(object):
    __instance_list = []
    __ffmpeg_path = None

    __idx = 1
    total_callback_function = None
    temp_path = None

    @classmethod
    def initialize(cls, __ffmpeg_path, temp_path, total_callback_function, max_pf_count=-1):
        cls.__ffmpeg_path = __ffmpeg_path
        cls.temp_path = temp_path
        cls.total_callback_function = total_callback_function
        cls.max_pf_count = max_pf_count

    # retry : 재시도 횟수 
    # max_error_packet_count : 이 숫자 초과시 중단
    # where : 호출 모듈
    def __init__(self, url, filename, save_path=None, max_pf_count=None, headers=None, timeout_minute=60, proxy=None, callback_id=None, callback_function=None):
        self.__idx = str(SupportFfmpeg.__idx)
        SupportFfmpeg.__idx += 1

        self.url = url
        self.filename = filename
        self.save_path = save_path
        self.max_pf_count = max_pf_count
        self.headers = headers
        self.timeout_minute = int(timeout_minute)
        self.proxy = proxy
        self.callback_id = callback_id
        if callback_id == None:
            self.callback_id = str(self.__idx)
        self.callback_function = callback_function

        self.temp_fullpath = os.path.join(self.temp_path, filename)
        self.save_fullpath = os.path.join(self.save_path, filename)
        self.thread = None
        self.process = None
        self.log_thread = None
        self.status = SupportFfmpeg.Status.READY
        self.duration = 0
        self.duration_str = ''
        self.current_duration = 0
        self.percent = 0
        #self.log = []
        self.current_pf_count = 0
        self.current_bitrate = ''
        self.current_speed = ''
        self.start_time = None
        self.end_time = None
        self.download_time = None
        self.start_event = threading.Event()
        self.exist = False
        self.filesize = 0
        self.filesize_str = ''
        self.download_speed = ''
        
        
        SupportFfmpeg.__instance_list.append(self)
        if len(SupportFfmpeg.__instance_list) > 30:
            for instance in SupportFfmpeg.__instance_list:
                if instance.thread is None and instance.status != SupportFfmpeg.Status.READY:
                    SupportFfmpeg.__instance_list.remove(instance)
                    break
                else:
                    logger.debug('remove fail %s %s', instance.thread, self.status)
        
    def start(self):  
        self.thread = threading.Thread(target=self.thread_fuction, args=())
        self.thread.start()
        self.start_time = datetime.now()
        return self.get_data()
    
    def start_and_wait(self):
        self.start()
        self.thread.join(timeout=60*70)

    def stop(self):
        try:
            self.status = SupportFfmpeg.Status.USER_STOP
            self.kill()
            #logger.warning('stop')
        except Exception as e:
            logger.error(f'Exception:{str(e)}')
            logger.error(traceback.format_exc())
    
    def kill(self):
        try:
            if self.process is not None and self.process.poll() is None:
                import psutil
                process = psutil.Process(self.process.pid)
                for proc in process.children(recursive=True):
                    proc.kill()
                process.kill()
        except Exception as e:
            logger.error(f'Exception:{str(e)}')
            logger.error(traceback.format_exc())
            

    def thread_fuction(self):
        try:
            header_count = 0
            if self.proxy is None:
                if self.headers is None:
                    command = [self.__ffmpeg_path, '-y', '-i', self.url, '-c', 'copy', '-bsf:a', 'aac_adtstoasc']
                else:
                    headers_command = []
                    tmp = ""
                    for key, value in self.headers.items():
                        if key.lower() == 'user-agent':
                            headers_command.append('-user_agent')
                            headers_command.append(f"{value}")
                            pass
                        else:
                            #headers_command.append('-headers')
                            if platform.system() == 'Windows':
                                tmp += f'{key}:{value}\r\n'
                                header_count += 1
                            else:
                                #tmp.append(f'{key}:{value}')
                                tmp += f'{key}:{value}\r\n'
                    if len(tmp) > 0:
                        headers_command.append('-headers')
                        headers_command.append(f'{tmp}')
                    command = [self.__ffmpeg_path, '-y'] + headers_command + ['-i', self.url, '-c', 'copy', '-bsf:a', 'aac_adtstoasc']
            else:
                command = [self.__ffmpeg_path, '-y', '-http_proxy', self.proxy, '-i', self.url, '-c', 'copy', '-bsf:a', 'aac_adtstoasc']

            
            if platform.system() == 'Windows':
                now = str(datetime.now()).replace(':', '').replace('-', '').replace(' ', '-')
                filename = ('%s' % now) + '.mp4'
                self.temp_fullpath = os.path.join(self.temp_path, filename)
                command.append(self.temp_fullpath)
            else:
                command.append(self.temp_fullpath)
            

            try:
                #logger.debug(' '.join(command))
                if os.path.exists(self.temp_fullpath):
                    for f in SupportFfmpeg.__instance_list:
                        if f.__idx != self.__idx and f.temp_fullpath == self.temp_fullpath and f.status in [SupportFfmpeg.Status.DOWNLOADING, SupportFfmpeg.Status.READY]:
                            self.status = SupportFfmpeg.Status.ALREADY_DOWNLOADING
                            return
            except:
                pass
            #logger.error(' '.join(command))
            command = SupportSubprocess.command_for_windows(command)

            if platform.system() == 'Windows' and header_count > 1:
                if os.environ.get('FF'):
                    from framework import F
                    batfilepath = os.path.join(F.config['path_data'], 'tmp', f"{time.time()}.bat")
                else:
                    batfilepath = f"{time.time()}.bat"
                tmp = command.replace('\r\n', '!CRLF!')
                text = f"""setlocal enabledelayedexpansion
SET CRLF=^


{tmp}"""
                SupportFile.write_file(batfilepath, text)
                command = batfilepath
            
            self.process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, encoding='utf8')

            self.status = SupportFfmpeg.Status.READY
            self.log_thread = threading.Thread(target=self.log_thread_fuction, args=())
            self.log_thread.start()
            self.start_event.wait(timeout=60)
            if self.log_thread is None:
                if self.status == SupportFfmpeg.Status.READY:
                    self.status = SupportFfmpeg.Status.ERROR
                self.kill()
            elif self.status == SupportFfmpeg.Status.READY:
                self.status = SupportFfmpeg.Status.ERROR
                self.kill()
            else:
                process_ret = self.process.wait(timeout=60*self.timeout_minute)
                # 2022-10-25
                time.sleep(3)
                logger.info(f"{process_ret=}")
                if process_ret is None: # timeout
                    if self.status != SupportFfmpeg.Status.COMPLETED and self.status != SupportFfmpeg.Status.USER_STOP and self.status != SupportFfmpeg.Status.PF_STOP:
                        self.status = SupportFfmpeg.Status.TIME_OVER
                        self.kill()
                else:
                    if self.status == SupportFfmpeg.Status.DOWNLOADING:
                        self.status = SupportFfmpeg.Status.FORCE_STOP
            self.end_time = datetime.now()
            self.download_time = self.end_time - self.start_time
            try:
                if self.status == SupportFfmpeg.Status.COMPLETED:
                    if self.save_fullpath != self.temp_fullpath:
                        if os.path.exists(self.save_fullpath):
                            os.remove(self.save_fullpath)
                        if platform.system() != 'Windows':
                            os.system('chmod 777 "%s"' % self.temp_fullpath)
                        shutil.move(self.temp_fullpath, self.save_fullpath)
                        self.filesize = os.stat(self.save_fullpath).st_size
                else:
                    if os.path.exists(self.temp_fullpath):
                        os.remove(self.temp_fullpath)
            except Exception as e:
                logger.error(f"Exception:{str(e)}")
                logger.error(traceback.format_exc())

            arg = {'type':'last', 'status':self.status, 'data' : self.get_data()}
            self.send_to_listener(**arg)
            self.process = None
            self.thread = None
        except Exception as e:
            logger.error(f'Exception:{str(e)}')
            logger.error(traceback.format_exc())
            try:
                self.status = SupportFfmpeg.Status.EXCEPTION
                arg = {'type':'last', 'status':self.status, 'data' : self.get_data()}
                self.send_to_listener(**arg)
            except:
                pass

            

    def log_thread_fuction(self):
        with self.process.stdout:
            for line in iter(self.process.stdout.readline, ''):
                line = line.strip()
                #logger.error(line)
                try:
                    if self.status == SupportFfmpeg.Status.READY:
                        if line.find('Server returned 404 Not Found') != -1 or line.find('Unknown error') != -1:
                            self.status = SupportFfmpeg.Status.WRONG_URL
                            self.start_event.set()
                        elif line.find('No such file or directory') != -1:
                            self.status = SupportFfmpeg.Status.WRONG_DIRECTORY
                            self.start_event.set()
                        else:
                            match = re.compile(r'Duration\:\s(\d{2})\:(\d{2})\:(\d{2})\.(\d{2})\,\sstart').search(line)
                            if match:
                                self.duration_str = '%s:%s:%s' % ( match.group(1), match.group(2), match.group(3))
                                self.duration = int(match.group(4))
                                self.duration += int(match.group(3)) * 100
                                self.duration += int(match.group(2)) * 100 * 60
                                self.duration += int(match.group(1)) * 100 * 60 * 60
                                if match:
                                    self.status = SupportFfmpeg.Status.READY
                                    arg = {'type':'status_change', 'status':self.status, 'data' : self.get_data()}
                                    self.send_to_listener(**arg)
                                continue
                            match = re.compile(r'time\=(\d{2})\:(\d{2})\:(\d{2})\.(\d{2})\sbitrate\=\s*(?P<bitrate>\d+).*?[$|\s](\s?speed\=\s*(?P<speed>.*?)x)?').search(line)
                            if match:
                                self.status = SupportFfmpeg.Status.DOWNLOADING
                                arg = {'type':'status_change', 'status':self.status, 'data' : self.get_data()}
                                self.send_to_listener(**arg)
                                self.start_event.set()
                    elif self.status == SupportFfmpeg.Status.DOWNLOADING:
                        if line.find('PES packet size mismatch') != -1:
                            self.current_pf_count += 1
                            if self.current_pf_count > self.max_pf_count:
                                self.status = SupportFfmpeg.Status.PF_STOP
                                self.kill()
                            continue
                        if line.find('HTTP error 403 Forbidden') != -1:
                            self.status = SupportFfmpeg.Status.HTTP_FORBIDDEN
                            self.kill()
                            continue
                        match = re.compile(r'time\=(\d{2})\:(\d{2})\:(\d{2})\.(\d{2})\sbitrate\=\s*(?P<bitrate>\d+).*?[$|\s](\s?speed\=\s*(?P<speed>.*?)x)?').search(line)
                        if match: 
                            self.current_duration = int(match.group(4))
                            self.current_duration += int(match.group(3)) * 100
                            self.current_duration += int(match.group(2)) * 100 * 60
                            self.current_duration += int(match.group(1)) * 100 * 60 * 60
                            try:
                                self.percent = int(self.current_duration * 100 / self.duration)
                            except: pass
                            self.current_bitrate = match.group('bitrate')
                            self.current_speed = match.group('speed')
                            self.download_time = datetime.now() - self.start_time
                            arg = {'type':'normal', 'status':self.status, 'data' : self.get_data()}
                            self.send_to_listener(**arg)
                            continue
                        match = re.compile(r'video\:\d*kB\saudio\:\d*kB').search(line)
                        if match:
                            self.status = SupportFfmpeg.Status.COMPLETED
                            self.end_time = datetime.now()
                            self.download_time = self.end_time - self.start_time
                            self.percent = 100
                            arg = {'type':'status_change', 'status':self.status, 'data' : self.get_data()}
                            self.send_to_listener(**arg)
                            continue
                except Exception as e:
                    logger.error(f'Exception:{str(e)}')
                    logger.error(traceback.format_exc())
        self.start_event.set()
        self.log_thread = None


    def get_data(self):
        data = {
            'url' : self.url,
            'filename' : self.filename,
            'max_pf_count' : self.max_pf_count,
            'callback_id' : self.callback_id,
            'temp_path' : self.temp_path,
            'save_path' : self.save_path,
            'temp_fullpath' : self.temp_fullpath,
            'save_fullpath' : self.save_fullpath,
            'status' : int(self.status),
            'status_str' : self.status.name,
            'status_kor' : str(self.status),
            'duration' : self.duration,
            'duration_str' : self.duration_str,
            'current_duration' : self.current_duration,
            'percent' : self.percent,
            'current_pf_count' : self.current_pf_count,
            'idx' : self.__idx,
            #'log' : self.log,
            'current_bitrate' : self.current_bitrate,
            'current_speed' : self.current_speed,
            'start_time' : '' if self.start_time is None else str(self.start_time).split('.')[0][5:],
            'end_time' : '' if self.end_time is None else str(self.end_time).split('.')[0][5:],
            'download_time' : '' if self.download_time is None else '%02d:%02d' % (self.download_time.seconds/60, self.download_time.seconds%60),
            'exist' : os.path.exists(self.save_fullpath),
        }                        
        if self.status == SupportFfmpeg.Status.COMPLETED:
            data['filesize'] = self.filesize
            data['filesize_str'] = SupportUtil.sizeof_fmt(self.filesize)
            if self.download_time.seconds != 0:
                data['download_speed'] = SupportUtil.sizeof_fmt(self.filesize/self.download_time.seconds, suffix='Bytes/Second')
            else:
                data['download_speed'] = '0Bytes/Second'
        return data

    def send_to_listener(self, **arg):
        if self.total_callback_function != None:
            self.total_callback_function(**arg)
        if self.callback_function is not None and self.callback_function != self.total_callback_function:
            arg['callback_id'] = self.callback_id
            self.callback_function(**arg)          


    @classmethod
    def stop_by_idx(cls, idx):
        try:
            for __instance in SupportFfmpeg.__instance_list:
                if __instance.__idx == idx:
                    __instance.stop()
                    break
        except Exception as e:
            logger.error(f'Exception:{str(e)}')
            logger.error(traceback.format_exc())
    

    @classmethod
    def stop_by_callback_id(cls, callback_id):
        try:
            for __instance in SupportFfmpeg.__instance_list:
                if __instance.callback_id == callback_id:
                    __instance.stop()
                    break
        except Exception as e:
            logger.error(f'Exception:{str(e)}')
            logger.error(traceback.format_exc())


    @classmethod
    def get_instance_by_idx(cls, idx):
        try:
            for __instance in SupportFfmpeg.__instance_list:
                if __instance.__idx == idx:
                    return __instance
        except Exception as e:
            logger.error(f'Exception:{str(e)}')
            logger.error(traceback.format_exc())

    

    @classmethod
    def get_instance_by_callback_id(cls, callback_id):
        try:
            for __instance in SupportFfmpeg.__instance_list:
                if __instance.callback_id == callback_id:
                    return __instance
        except Exception as e:
            logger.error(f'Exception:{str(e)}')
            logger.error(traceback.format_exc())
        
    @classmethod
    def all_stop(cls):
        try:
            for __instance in SupportFfmpeg.__instance_list:
                __instance.stop()
        except Exception as e:
            logger.error(f'Exception:{str(e)}')
            logger.error(traceback.format_exc())

    @classmethod
    def get_list(cls):
        return cls.__instance_list






    class Status(enum.Enum):
        READY = 0
        WRONG_URL = 1
        WRONG_DIRECTORY = 2
        EXCEPTION = 3
        ERROR = 4
        HTTP_FORBIDDEN = 11
        
        DOWNLOADING = 5

        USER_STOP = 6
        COMPLETED = 7
        TIME_OVER = 8
        PF_STOP = 9
        FORCE_STOP = 10 #강제중단
        ALREADY_DOWNLOADING = 12 #이미 목록에 있고 다운로드중

        def __int__(self):
            return self.value

        def __str__(self):
            kor = ['준비', 'URL에러', '폴더에러', '실패(Exception)', '실패(에러)', '다운로드중', '사용자중지', '완료', '시간초과', 'PF중지', '강제중지',
            '403에러', '임시파일이 이미 있음']
            return kor[int(self)]
        
        def __repr__(self):
            return self.name
        
        @staticmethod
        def get_instance(value):
            tmp = [ 
                SupportFfmpeg.Status.READY, 
                SupportFfmpeg.Status.WRONG_URL, 
                SupportFfmpeg.Status.WRONG_DIRECTORY, 
                SupportFfmpeg.Status.EXCEPTION, 
                SupportFfmpeg.Status.ERROR,
                SupportFfmpeg.Status.DOWNLOADING, 
                SupportFfmpeg.Status.USER_STOP, 
                SupportFfmpeg.Status.COMPLETED, 
                SupportFfmpeg.Status.TIME_OVER, 
                SupportFfmpeg.Status.PF_STOP, 
                SupportFfmpeg.Status.FORCE_STOP, 
                SupportFfmpeg.Status.HTTP_FORBIDDEN, 
                SupportFfmpeg.Status.ALREADY_DOWNLOADING ]
            return tmp[value]


