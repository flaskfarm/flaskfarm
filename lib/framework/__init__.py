try:
    import yaml
except:
    import os
    try:
        os.system("pip install pyyaml")
    except:
        pass
    
from .init_main import Framework
from .version import VERSION

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
from flask_login import login_required
from support import d

from .init_declare import User, check_api
from .scheduler import Job

frame.initialize_system()
from system.setup import SystemModelSetting

frame.initialize_plugin()
 