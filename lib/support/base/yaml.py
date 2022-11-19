import os
import traceback

import yaml

from . import logger


class SupportYaml(object):
    @classmethod
    def write_yaml(cls, filepath, data):
        with open(filepath, 'w', encoding='utf8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)

    @classmethod
    def read_yaml(self, filepath):
        with open(filepath, encoding='utf8') as file:
            data = yaml.load(file, Loader=yaml.FullLoader)
        return data


    @classmethod
    def copy_section(cls, source_file, target_file, section_name):
        from support import SupportFile
        try:
            if os.path.exists(source_file) == False:
                return 'not_exist_source_file'
            if os.path.exists(target_file) == False:
                return 'not_exist_target_file'
            lines = SupportFile.read_file(source_file).split('\n')
            section = {}
            current_section_name = None
            current_section_data = None

            for line in lines:
                line = line.strip()
                if line.startswith('# SECTION START : '):
                    current_section_name = line.split(':')[1].strip()
                    current_section_data = []
                if current_section_data is not None:
                    current_section_data.append(line)
                if line.startswith('# SECTION END'):
                    section[current_section_name] = current_section_data
                    current_section_name = current_section_data = None

            if section_name not in section:
                return 'not_include_section'
            
            data = '\n'.join(section[section_name])
            source_data = SupportFile.read_file.read(target_file)
            source_data = source_data + f"\n{data}\n"
            SupportFile.write_file(source_data, target_file)
            return 'success'
        except Exception as e: 
            logger.error(f"Exception:{str(e)}")
            logger.error(traceback.format_exc())
            return 'exception'