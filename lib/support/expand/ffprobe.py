import traceback

from support import SupportSubprocess, logger


class SupportFfprobe:
    @classmethod
    def ffprobe(cls, filepath, ffprobe_path='ffprobe', option=None):
        try:
            command = [ffprobe_path, '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', filepath]
            if option is not None:
                command += option
            logger.warning(' '.join(command))
            ret = SupportSubprocess.execute_command_return(command, format='json')
            return ret['log']
        except Exception as e: 
            logger.error(f"Exception:{str(e)}")
            logger.error(traceback.format_exc())    