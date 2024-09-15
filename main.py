try:
    from gevent import monkey;monkey.patch_all()
    print('[MAIN] gevent mokey patch!!')
except:
    print('[MAIN] gevent not installed!!')
import os
import sys
import traceback

try:
    import platform
    cmd = 'export'
    if platform.system() == 'Windows':
        cmd = 'set'
    os.system(f"{cmd} CELERYD_HIJACK_ROOT_LOGGER=false")
    os.system(f"{cmd} C_FORCE_ROOT=true")
except: pass

try:
    if platform.system() == 'Windows':
        del os.environ['SSLKEYLOGFILE']
except: pass

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib'))

try:
    import importlib.metadata
    package_name = 'python-socketio'
    version = importlib.metadata.version(package_name)
    if int(version.replace('.', '')) < 580:
        os.system(f"pip install --upgrade {package_name}")
except:
    pass


try:
    # 2024.06.13 
    from framework import initiaize
    frame = initiaize()
    
    # flaskfarm.main : 패키지로 실행. 패키지로 celry 실행 체크
    if __name__ in ['__main__', 'flaskfarm.main'] and sys.argv[0].endswith('celery') == False:
        frame.start()
    else:  
        app = frame.app
        celery = frame.celery
except Exception as exception:
    print(str(exception))  
    print(traceback.format_exc())
