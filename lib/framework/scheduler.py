import threading
import traceback
from datetime import datetime, timedelta
from random import randint

from apscheduler.jobstores.base import JobLookupError
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone


class Scheduler(object):
    job_list = []
    first_run_check_thread = None
    def __init__(self, frame):
        self.frame = frame
        self.logger = frame.logger
        try:
            if frame.config['use_gevent']:
                from apscheduler.schedulers.gevent import GeventScheduler
                self.sched = GeventScheduler(timezone='Asia/Seoul')
            else:
                raise Exception('')
        except:
            from apscheduler.schedulers.background import BackgroundScheduler
            self.sched = BackgroundScheduler(timezone='Asia/Seoul')
        self.sched.start()
        self.logger.info('SCHEDULER start..')

    def first_run_check_thread_function(self):
        try:
            #time.sleep(60)
            #for i in range(5):
            flag_exit = True
            for job_instance in self.job_list:
                if not job_instance.run:
                    continue
                if job_instance.count == 0 and not job_instance.is_running and job_instance.is_interval:
                #if job_instance.count == 0 and not job_instance.is_running:
                    job = self.sched.get_job(job_instance.job_id) 
                    if job is not None:
                        self.logger.warning('job_instance : %s', job_instance.plugin)
                        self.logger.warning('XX job re-sched:%s', job)
                        flag_exit = False
                        tmp = randint(1, 20)
                        job.modify(next_run_time=datetime.now(timezone('Asia/Seoul')) + timedelta(seconds=tmp))
                        #break
                    else:
                        pass
            if flag_exit:
                self.remove_job("scheduler_check")
            #time.sleep(30)
        except Exception as e: 
            self.logger.error(f"Exception:{str(e)}")
            self.logger.error(traceback.format_exc())
    
    def shutdown(self):
        self.sched.shutdown()

    def kill_scheduler(self, job_id):
        try:
            self.sched.remove_job(job_id)
        except JobLookupError as err:
            self.logger.debug("fail to stop Scheduler: {err}".format(err=err))
            self.logger.debug(traceback.format_exc())
        

    
    def add_job_instance(self, job_instance, run=True):
        if self.frame.config['run_flask']:
            if not self.is_include(job_instance.job_id):
                job_instance.run = run
                Scheduler.job_list.append(job_instance)
                if job_instance.is_interval:
                    self.sched.add_job(job_instance.job_function, 'interval', minutes=job_instance.interval, seconds=job_instance.interval_seconds, id=job_instance.job_id, args=(None))
                elif job_instance.is_cron:
                    self.sched.add_job(job_instance.job_function, CronTrigger.from_crontab(job_instance.interval), id=job_instance.job_id, args=(None))
                job = self.sched.get_job(job_instance.job_id) 
                if run and job_instance.is_interval:
                    tmp = randint(5, 20)
                    job.modify(next_run_time=datetime.now(timezone('Asia/Seoul')) + timedelta(seconds=tmp))

    def execute_job(self, job_id):
        self.logger.debug('execute_job:%s', job_id)
        job = self.sched.get_job(job_id) 
        tmp = randint(5, 20)
        job.modify(next_run_time=datetime.now(timezone('Asia/Seoul')) + timedelta(seconds=tmp))
         
    
    def is_include(self, job_id):
        job = self.sched.get_job(job_id) 
        return (job is not None)
    
    def remove_job(self, job_id):
        try:
            if self.is_include(job_id):
                self.sched.remove_job(job_id)
                job = self.get_job_instance(job_id)
                if not job.is_running:
                    self.remove_job_instance(job_id)
                self.logger.debug('remove job_id:%s', job_id)
            return True
        except JobLookupError as err:
            self.logger.debug("fail to remove Scheduler: {err}".format(err=err))
            self.logger.debug(traceback.format_exc())
            return False

     
    def get_job_instance(self, job_id):
        for job in Scheduler.job_list:
            if job.job_id == job_id:
                return job
    
    def is_running(self, job_id):
        job = self.get_job_instance(job_id)
        if job is None:
            return False
        else:
            return job.is_running

    # job에서만 호출한다..
    def remove_job_instance(self, job_id):
        # function이 실행중일때 제거하면..
        # 실행중이나 목록에서 빠져버린다..
        for job in Scheduler.job_list:
            if job.job_id == job_id:
                Scheduler.job_list.remove(job)
                self.logger.debug('remove_job_instance : %s', job_id)
                break


    def get_job_list_info(self):
        
        ret = []
        idx = 0
        job_list = self.sched.get_jobs()
        #logger.debug('len jobs %s %s', len(jobs), len(Scheduler.job_list))
        for j in job_list:
            idx += 1
            entity = {}
            entity['no'] = idx
            entity['id'] = j.id
            entity['next_run_time'] = j.next_run_time.strftime('%m-%d %H:%M:%S')
            remain = (j.next_run_time - datetime.now(timezone('Asia/Seoul')))
            tmp = ''
            if remain.days > 0:
                tmp += '%s일 ' % (remain.days)
            remain = remain.seconds
            if remain//3600 > 0:
                tmp += '%s시간 ' % (remain//3600)
            remain = remain % 3600
            if remain // 60 > 0:
                tmp += '%s분 ' % (remain//60)
            tmp += '%s초' % (remain%60)
            #entity['remain_time'] = (j.next_run_time - datetime.now(timezone('Asia/Seoul'))).seconds
            entity['remain_time'] = tmp
            job = self.get_job_instance(j.id)
            if job is not None:
                entity['count'] = job.count
                entity['plugin'] = job.plugin
                if job.is_cron:
                    entity['interval'] = job.interval
                elif job.interval == 9999:
                    entity['interval'] = '항상 실행'
                    entity['remain_time'] = ''
                else:
                    entity['interval'] = '%s분 %s초' % (job.interval, job.interval_seconds)
                entity['is_running'] = job.is_running
                entity['description'] = job.description
                entity['running_timedelta'] = job.running_timedelta.seconds if job.running_timedelta is not None else '-'
                if entity['running_timedelta'] != '-':
                    tmp = entity['running_timedelta']
                    _min = entity['running_timedelta'] / 60
                    _sec = entity['running_timedelta'] % 60
                    entity['running_timedelta'] = "%2d분 %2d초" % (_min, _sec)
                entity['make_time'] = job.make_time.strftime('%m-%d %H:%M:%S')
                entity['run'] = job.run
            else:
                entity['count'] = ''
                entity['plugin'] = ''
                entity['interval'] = ''
                entity['is_running'] = ''
                entity['description'] = ''
                entity['running_timedelta'] = ''
                entity['make_time'] = ''
                entity['run'] = True
            
            ret.append(entity)
        return ret







class Job(object):
    def __init__(self, plugin, job_id, interval, target_function, description, args=None):
        self.plugin = plugin
        self.job_id = job_id
        self.interval = '%s' % interval
        self.interval_seconds = randint(1, 59)
        self.target_function = target_function
        self.description = description
        self.is_running = False
        self.thread = None
        self.start_time = None
        self.end_time = None
        self.running_timedelta = None
        self.status = None
        self.count = 0
        self.make_time = datetime.now(timezone('Asia/Seoul'))
        if len(self.interval.strip().split(' ')) == 5:
            self.is_cron = True
            self.is_interval = False
        else:
            self.is_cron = False
            self.is_interval = True
        if self.is_interval:
            if isinstance(self.interval, str):
                self.interval = int(self.interval)
        self.args = args
        # true이고 interval이면 바로 실행
        # false이면 스케쥴링시간이 되면 실행
        # add_job_instance에서 true이면 20초 이내에 실행하려고 함.
        # false이면 넣을 때는 실행하지 않고 다음 주기때 실행
        self.run = True

    def job_function(self):
        try:
            from framework import F
            self.is_running = True
            self.start_time = datetime.now(timezone('Asia/Seoul'))
            if self.args is None:
                self.thread = threading.Thread(target=self.target_function, args=())
            else:
                self.thread = threading.Thread(target=self.target_function, args=self.args)
            self.thread.daemon = True
            self.thread.start()
            F.socketio.emit('notify', {'type':'success', 'msg':f"{self.description}<br>작업을 시작합니다." }, namespace='/framework')
            self.thread.join()
            F.socketio.emit('notify', {'type':'success', 'msg':f"{self.description}<br>작업이 종료되었습니다." }, namespace='/framework')
            self.end_time = datetime.now(timezone('Asia/Seoul'))
            self.running_timedelta = self.end_time - self.start_time
            self.status = 'success'
            if not F.scheduler.is_include(self.job_id):
                F.scheduler.remove_job_instance(self.job_id)
            self.count += 1
        except Exception as e: 
            self.status = 'exception'
            F.logger.error(f"Exception:{str(e)}")
            F.logger.error(traceback.format_exc())
        finally:
            self.is_running = False
            

        

