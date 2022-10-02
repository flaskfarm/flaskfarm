try:
    from gevent import monkey;monkey.patch_all()
    print('[MAIN] gevent mokey patch!!')
except:
    print('[MAIN] gevent not installed!!')

import os, sys, traceback
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib'))
sys.path.insert(1, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib2'))

try:
    from framework import frame
    if __name__ == '__main__':
        frame.start()
    else:  
        app = frame.app
        celery = frame.celery
except Exception as exception:
    print(str(exception))  
    print(traceback.format_exc())
