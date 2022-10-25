__menu = {
    'uri' : __package__,
    'name': '설정',
    'list': [
        {
            'uri': 'setting',
            'name': '일반설정',
            'list': [
                {'uri': 'basic', 'name': '기본'},
                {'uri': 'auth', 'name': '인증'},
                {'uri': 'web', 'name': '웹'},
                {'uri': 'menu', 'name': '메뉴 구성'},                
                {'uri': 'config', 'name': 'config.yaml 파일'},
                {'uri': 'export', 'name': 'export.sh 파일'},
                {'uri': 'celery', 'name': '비동기 작업(celery)'},
                {'uri': 'notify', 'name': '알림'},
            ],
        },
        {
            'uri': 'plugin', 
            'name': '플러그인',
            'list': [
                #{'uri': 'setting', 'name': '설정'},
                {'uri': 'list', 'name': '로딩 플러그인'},
                #{'uri': 'all', 'name': '플러그인 목록'},
            ],
        },
        {
            'uri': 'tool',
            'name': '시스템 툴',
            'list': [
                {'uri': 'command', 'name': 'Command'},
                {'uri': 'upload', 'name': '업로드'},
                {'uri': 'python', 'name': 'Python'},
                #{'uri': 'db', 'name': 'DB'},
                #{'uri': 'crypt', 'name': '암호화'},
            ]
        },
        {
            'uri': 'all_log',
            'name': '전체 로그'
        }
    ]
}


import os

from framework import F

export = os.path.join(F.config['path_app'], 'export.sh')
if os.path.exists(export) == False:
    for mod in __menu['list']:
        if mod['uri'] == 'setting':
            del mod['list'][5]




setting = {
    'filepath' : __file__,
    'use_db': True,
    'use_default_setting': True,
    'home_module': 'setting',
    'menu': __menu,
    'setting_menu': None,
    'default_route': 'normal',
}

try:
    from plugin import *
    P = create_plugin_instance(setting)

    SystemModelSetting = P.ModelSetting
    from .mod_home import ModuleHome
    from .mod_log import ModuleLog
    from .mod_plugin import ModulePlugin
    from .mod_route import ModuleRoute
    from .mod_setting import ModuleSetting
    from .mod_tool import ModuleTool
    P.set_module_list([ModuleHome, ModuleRoute, ModuleSetting, ModulePlugin, ModuleTool, ModuleLog])

except Exception as e:
    F.logger.error(f'Exception:{str(e)}')
    F.logger.error(traceback.format_exc())
