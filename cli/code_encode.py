
import argparse
import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'lib'))

from support import SupportFile, SupportSC, logger


class CodeEncode:
    def start_folder(self, folderpath):
        for name in os.listdir(folderpath):
            filepath = os.path.join(folderpath, name)
            if os.path.isfile(filepath) and name not in ['setup.py', '__init__.py'] and name.endswith('.py'):
                self.encode_file(filepath)

    def encode_file(self, filepath):
        if filepath.endswith(".py") == False:
            logger.info("is not .py file")
            return
        text = SupportFile.read_file(filepath)
        data = SupportSC.encode(text, 1)
        SupportFile.write_file(filepath + 'f', data)
        logger.info(f"Create {os.path.basename(filepath + 'f')}")


    def process_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--mode', default='encode')
        parser.add_argument('--source', required=True, help=u'absolute path. folder or file')
        args = parser.parse_args()
        if SupportSC.LIBRARY_LOADING == False:
            logger.error("sc import fail")
            return
        if os.path.exists(args.source):
            if os.path.isdir(args.source):
                self.start_folder(args.source)
            elif os.path.isfile(args.source):
                self.encode_file(args.source)
        else:
            logger.error("wrong source path!!")


if __name__== "__main__":
    CodeEncode().process_args()

# python C:\work\FlaskFarm\flaskfarm\cli\code_encode.py --source=C:\work\FlaskFarm\data\LOADING\sjva
