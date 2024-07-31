from .init_main import Framework
from .version import VERSION

# 2024.06.13 
# 잘못된 설계로 인해 import 만으로 초기화 되버려 lib을 사용할 수 없다.
# 분리.

F = None
frame = None
logger = None
app = None
celery = None
db = None
scheduler = None
socketio = None
rd = None
path_app_root = None
path_data = None
get_logger = None
SystemModelSetting = None

def initiaize():
    global F
    global frame 
    global logger
    global app
    global celery
    global db
    global scheduler
    global socketio
    global path_app_root
    global path_data
    global get_logger
    global SystemModelSetting

    F = Framework.get_instance()
    frame = F
    logger = frame.logger
    app = frame.app
    celery = frame.celery
    db = frame.db
    scheduler = frame.scheduler
    socketio = frame.socketio
    rd = frame.rd
    path_app_root = frame.path_app_root
    path_data = frame.path_data
    get_logger = frame.get_logger

    frame.initialize_system()
    from system.setup import SystemModelSetting as SS
    SystemModelSetting = SS
    frame.initialize_plugin()
    return frame

from flask_login import login_required
from support import d

from .init_declare import User, check_api
from .scheduler import Job
