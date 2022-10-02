VERSION="4.0.0"
from support import d
from .init_main import Framework
frame = Framework.get_instance()
F = frame
logger = frame.logger
app = frame.app
celery = frame.celery
db = frame.db
scheduler = frame.scheduler
socketio = frame.socketio
path_app_root = frame.path_app_root
path_data = frame.path_data
get_logger = frame.get_logger

from .init_declare import check_api, User
from flask_login import login_required
from .scheduler import Job

frame.initialize_system()
from system.setup import SystemModelSetting

frame.initialize_plugin()
