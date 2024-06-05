import re

from framework import F


def get_menu(full_query):
    match = re.compile(r'\/(?P<package_name>.*?)\/(?P<module_name>.*?)\/manual\/(?P<sub2>.*?)($|\?)').match(full_query)
    if match:
        return match.group('package_name'), match.group('module_name'), f"manual/{match.group('sub2')}"

    match = re.compile(r'\/(?P<menu>.*?)\/manual\/(?P<sub2>.*?)($|\?)').match(full_query)
    if match:
        return match.group('menu'), 'manual', match.group('sub2')

    match = re.compile(r'\/(?P<menu>.*?)\/(?P<sub>.*?)\/(?P<sub2>.*?)($|\/|\?)').match(full_query)
    if match:
        return match.group('menu'), match.group('sub'), match.group('sub2')

    match = re.compile(r'\/(?P<menu>.*?)\/(?P<sub>.*?)($|\/|\?)').match(full_query)
    if match: 
        return match.group('menu'), match.group('sub'), None

    match = re.compile(r'\/(?P<menu>.*?)($|\/|\?)').match(full_query)
    if match:
        return match.group('menu'), None , None
    return 'home', None, None
 


def get_theme():
    return F.SystemModelSetting.get('theme')

#def get_login_status():
#    if current_user is None:
#        return False
#    return current_user.is_authenticated

def get_web_title():
    try:
        return F.SystemModelSetting.get('web_title')
    except:
        return 'Home'


def is_https():
    return (F.SystemModelSetting.get('ddns').find('https://') != -1)


def jinja_initialize(app):
    #from .init_menu import get_menu_map, get_plugin_menu
    from .init_menu import MenuManager
    app.jinja_env.globals.update(get_menu=get_menu)
    app.jinja_env.globals.update(get_theme=get_theme)
    app.jinja_env.globals.update(get_menu_map=MenuManager.get_menu_map)
    app.jinja_env.globals.update(get_setting_menu=MenuManager.get_setting_menu)
    app.jinja_env.globals.update(get_web_title=get_web_title)
    app.jinja_env.globals.update(dropzone=F.dropzone)

    app.jinja_env.filters['get_menu'] = get_menu
    app.jinja_env.filters['get_theme'] = get_theme
    app.jinja_env.filters['get_menu_map'] = MenuManager.get_menu_map
    app.jinja_env.filters['get_setting_menu'] = MenuManager.get_setting_menu
    app.jinja_env.filters['get_web_title'] = get_web_title

    app.jinja_env.auto_reload = True
    app.jinja_env.add_extension('jinja2.ext.loopcontrols')
