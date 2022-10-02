import traceback
from framework import db, get_logger
from framework.util import Util

logger = get_logger(__package__)

from plugin.model_setting import get_model_setting
ModelSetting = get_model_setting(__package__, logger)
