# -*- coding: utf-8 -*-
#########################################################
import json
import os
import platform
import subprocess
import sys
import traceback

from framework import app, logger, path_data

from ..support.base.subprocess import ToolSubprocess


class ToolFfmpeg(object):

    @classmethod
    def ffprobe(cls, filepath, ffprobe_path='ffprobe', option=None):
        try:
            command = [ffprobe_path, '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', filepath]
            if option is not None:
                command += option
            logger.warning(' '.join(command))
            ret = ToolSubprocess.execute_command_return(command, format='json')
            return ret
        except Exception as e: 
            logger.error(f"Exception:{str(e)}")
            logger.error(traceback.format_exc())

