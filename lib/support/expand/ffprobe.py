import traceback

from support import SupportSubprocess, logger


class SupportFfprobe:
    __ffprobe_path = 'ffprobe'

    @classmethod
    def initialize(cls, __ffprobe_path):
        cls.__ffprobe_path = __ffprobe_path
        
    @classmethod
    def ffprobe(cls, filepath, ffprobe_path=None, option=None):
        try:
            if ffprobe_path == None:
                ffprobe_path = cls.__ffprobe_path

            command = [ffprobe_path, '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', filepath]
            if option is not None:
                command += option
            logger.warning(' '.join(command))
            ret = SupportSubprocess.execute_command_return(command, format='json')
            return ret['log']
        except Exception as e: 
            logger.error(f"Exception:{str(e)}")
            logger.error(traceback.format_exc())    