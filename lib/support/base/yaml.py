import yaml

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
