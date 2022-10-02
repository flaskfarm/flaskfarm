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
                {'uri': 'env', 'name': '시스템'},
                {'uri': 'menu', 'name': '메뉴'},
                {'uri': 'notify', 'name': '알림'},
                {'uri': 'crypt', 'name': '암호화'},
            ],
        },
        {
            'uri': 'plugin',
            'name': '플러그인'
        },
        {
            'uri': 'python',
            'name': 'Python'
        },
        {
            'uri': 'db',
            'name': 'DB'
        },
        {
            'uri': 'log',
            'name': '로그'
        }
    ]
}


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
    from .mod_setting import ModuleSetting
    from .mod_home import ModuleHome
    from .mod_route import ModuleRoute
    
    P.set_module_list([ModuleSetting, ModuleHome, ModuleRoute])

except Exception as e:
    P.logger.error(f'Exception:{str(e)}')
    P.logger.error(traceback.format_exc())