import argparse
import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'lib'))

from support import SupportFile, logger


class ChangeUI:
    def change(self, target, old, new):
        if target == 'macro':
            target_filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'lib', 'framework', 'templates', 'macro.html')
            text = SupportFile.read_file(target_filepath)
            SupportFile.write_file(target_filepath, text.replace(old, new))

    def process_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--target', default='macro')
        parser.add_argument('--old', default='btn-outline-primary')
        parser.add_argument('--new', required=True)
        args = parser.parse_args()
        self.change(args.target, args.old, args.new)

if __name__== "__main__":
    ChangeUI().process_args()
