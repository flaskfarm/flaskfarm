import os
import shutil
import traceback

from framework import F, logger
from support import SupportYaml, d


class MenuManager:
    menu_map = None

    @classmethod
    def __load_menu_yaml(cls):
        try:
            menu_yaml_filepath = os.path.join(F.config['path_data'], 'db', 'menu.yaml')
            if os.path.exists(menu_yaml_filepath) == False:
                shutil.copy(
                    os.path.join(F.config['path_app'], 'files', 'menu.yaml.template'),
                    menu_yaml_filepath
                )
            cls.menu_map = SupportYaml.read_yaml(menu_yaml_filepath)
        except Exception as e: 
            logger.error(f"Exception:{str(e)}")
            logger.error(traceback.format_exc())
            cls.menu_map = SupportYaml.read_yaml(os.path.join(F.config['path_app'], 'files', 'menu.yaml.template'))
        

    @classmethod
    def init_menu(cls):
        cls.__load_menu_yaml()
        if cls.__init_menu() == False:
            cls.menu_map = SupportYaml.read_yaml(os.path.join(F.config['path_app'], 'files', 'menu.yaml.template'))
            cls.__init_menu()

    @classmethod
    def __init_menu(cls):
        try:
            from .init_plugin import PluginManager
            plugin_menus = PluginManager.plugin_menus
            copy_map = [] 
            for category in cls.menu_map:
                if 'uri' in category:
                    if category['uri'] in plugin_menus:
                        plugin_menus[category['uri']]['match'] = True
                        copy_map.append(plugin_menus[category['uri']]['menu'])
                    else:
                        copy_map.append(category)
                    continue
                cate_count = 0  

                tmp_cate_list = []
                for item in category['list']:
                    if item['uri'] in plugin_menus:
                        plugin_menus[item['uri']]['match'] = True
                        tmp_cate_list.append(plugin_menus[item['uri']]['menu'])
                        cate_count += 1
                    elif item['uri'].startswith('http'):
                        tmp_cate_list.append({
                            'uri': item['uri'],
                            'name': item['name'],
                            'target': item.get('target', '_blank')
                        })
                        cate_count += 1
                    elif (len(item['uri'].split('/')) > 1 and item['uri'].split('/')[0] in plugin_menus) or item['uri'].startswith('javascript') or item['uri'] in ['-']:
                        tmp_cate_list.append({
                            'uri': item['uri'],
                            'name': item.get('name', ''),
                        })
                        cate_count += 1
                    elif item['uri'] == 'setting':
                        if len(PluginManager.setting_menus) > 0:
                            tmp_cate_list.append({
                                'uri': item['uri'],
                                'name': item.get('name', ''),
                                'list': PluginManager.setting_menus
                            })
                    
                if cate_count > 0:
                    copy_map.append({
                        'name': category['name'],
                        'list': tmp_cate_list,
                        'count': cate_count
                    })
            cls.menu_map = copy_map
                
            make_dummy_cate = False
            for name, plugin_menu in plugin_menus.items():
                #F.logger.info(d(plugin_menu))
                #if 'uri' not in plugin_menu['menu']:
                #    continue
                if plugin_menu['match'] == False:
                    if make_dummy_cate == False:
                        make_dummy_cate = True
                        cls.menu_map.insert(len(cls.menu_map)-1, {
                            'name':'미분류', 'count':0, 'list':[]
                        })

                    c = cls.menu_map[-2]
                    c['count'] += 1
                    c['list'].append(plugin_menu['menu'])
            return True
        except Exception as e: 
            logger.error(f"Exception:{str(e)}")
            logger.error(traceback.format_exc())
            return False
        
        #F.logger.warning(d(cls.menu_map))


    @classmethod
    def get_menu_map(cls):
        #F.logger.warning(d(cls.menu_map))
        return cls.menu_map
