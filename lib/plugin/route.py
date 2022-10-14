import json
import os
import traceback

from flask import jsonify, redirect, render_template, request
from flask_login import login_required
from framework import F
from support import AlchemyEncoder


def default_route(P):
    @P.blueprint.route('/')
    def home():
        if P.ModelSetting is not None:
            tmp = P.ModelSetting.get('recent_menu_plugin')
            if tmp is not None and tmp != '':
                tmps = tmp.split('|')
                if len(tmps) == 2:
                    return redirect('/{package_name}/{sub}/{sub2}'.format(package_name=P.package_name, sub=tmps[0], sub2=tmps[1]))
                elif len(tmps) == 1 and not (P.package_name =='system' and tmps[0] == 'logout'):
                    return redirect('/{package_name}/{sub}'.format(package_name=P.package_name, sub=tmps[0]))

        return redirect('/{package_name}/{home_module}'.format(package_name=P.package_name, home_module=P.home_module))
        
    @P.blueprint.route('/<sub>', methods=['GET', 'POST'])
    @login_required
    def first_menu(sub):
        try:
            if P.ModelSetting is not None and (P.package_name == 'system' and sub != 'home'):
                P.ModelSetting.set('recent_menu_plugin', '{}'.format(sub))
            for module in P.module_list:
                if sub == module.name:
                    first_menu =  module.get_first_menu()
                    if first_menu:
                        return redirect('/{package_name}/{sub}/{first_menu}'.format(package_name=P.package_name, sub=sub, first_menu=module.get_first_menu()))
                    else:
                        return module.process_menu(None, request)
            if sub == 'log':
                return render_template('log.html', package=P.package_name)
            elif sub == 'manual':
                #return redirect(f"/{P.package_name}/manual/{P.menu['second']['manual'][0][0]}")
                try:
                    return redirect(f"/{P.package_name}/manual/{P.menu['sub2']['manual'][0][0]}")
                except:
                    return redirect(f"/{P.package_name}/manual/{P.get_first_manual_path()}")
                    
            return render_template('sample.html', title='%s - %s' % (P.package_name, sub))
        except Exception as exception:
            P.logger.error('Exception:%s', exception)
            P.logger.error(traceback.format_exc())
    
    @P.blueprint.route('/manual/<path:path>', methods=['GET', 'POST'])
    @login_required
    def manual(path):
        try:
            plugin_root = os.path.dirname(P.blueprint.template_folder)
            filepath = os.path.join(plugin_root,  *path.split('/'))
            from tool_base import ToolBaseFile
            data = ToolBaseFile.read(filepath)
            return render_template('manual.html', data=data)
        except Exception as exception:
            P.logger.error('Exception:%s', exception)
            P.logger.error(traceback.format_exc())

    @P.blueprint.route('/<sub>/<sub2>', methods=['GET', 'POST'])
    @login_required
    def second_menu(sub, sub2):
        if P.ModelSetting is not None:
            P.ModelSetting.set('recent_menu_plugin', '{}|{}'.format(sub, sub2))
        try:
            for module in P.module_list:
                if sub == module.name:
                    return module.process_menu(sub2, request)
            if sub == 'log':
                return render_template('log.html', package=P.package_name)
            return render_template('sample.html', title='%s - %s' % (P.package_name, sub))
        except Exception as exception:
            P.logger.error('Exception:%s', exception)
            P.logger.error(traceback.format_exc())

    #########################################################
    # For UI
    #########################################################
    @P.blueprint.route('/ajax/<sub>', methods=['GET', 'POST'])
    @login_required
    def ajax(sub):
        P.logger.debug('AJAX %s %s', P.package_name, sub)
        try:
            # global
            if sub == 'setting_save':
                ret, change_list = P.ModelSetting.setting_save(request)
                for module in P.module_list:
                    module.setting_save_after(change_list)
                return jsonify(ret)
            elif sub == 'scheduler':
                sub = request.form['sub']
                go = request.form['scheduler']
                P.logger.debug('scheduler :%s', go)
                if go == 'true':
                    P.logic.scheduler_start(sub)
                else:
                    P.logic.scheduler_stop(sub)
                return jsonify(go)
            elif sub == 'reset_db':
                sub = request.form['sub']
                ret = P.logic.reset_db(sub)
                return jsonify(ret)
            elif sub == 'one_execute':
                sub = request.form['sub']
                ret = P.logic.one_execute(sub)
                return jsonify(ret)
            elif sub == 'immediately_execute':
                sub = request.form['sub']
                ret = P.logic.immediately_execute(sub)
                return jsonify(ret)
        except Exception as exception: 
            P.logger.error('Exception:%s', exception)
            P.logger.error(traceback.format_exc())  

    @P.blueprint.route('/ajax/<mod>/<cmd>', methods=['GET', 'POST'])
    @login_required
    def second_ajax(mod, cmd):
        try:
            for module in P.module_list:
                if mod == module.name:
                    if cmd == 'command':
                        return module.process_command(request.form['command'], request.form.get('arg1'), request.form.get('arg2'), request.form.get('arg3'), request)
                    else:
                        return module.process_ajax(cmd, request)

        except Exception as exception: 
            P.logger.error('Exception:%s', exception)
            P.logger.error(traceback.format_exc())

    @P.blueprint.route('/ajax/<module_name>/<page_name>/<command>', methods=['GET', 'POST'])
    @login_required
    def sub_ajax(module_name, page_name, command):
        try:
            ins_module = P.get_module(module_name)
            ins_page = ins_module.get_page(page_name)
            if ins_page != None:
                if command == 'scheduler':
                    #sub = page_name
                    go = request.form['scheduler']
                    P.logger.debug('scheduler :%s', go)
                    if go == 'true':
                        P.logic.scheduler_start_sub(module_name, page_name)
                    else:
                        P.logic.scheduler_stop_sub(module_name, page_name)
                    return jsonify(go)
                #elif command == 'reset_db':
                #    sub = request.form['sub']
                #    ret = P.logic.reset_db(sub)
                #    return jsonify(ret)
                elif command == 'one_execute':
                    ret = P.logic.one_execute_sub(module_name, page_name)
                    return jsonify(ret)
                elif command == 'immediately_execute':
                    ret = P.logic.immediately_execute_sub(module_name, page_name)
                    return jsonify(ret)
                elif command == 'command':
                    return ins_page.process_command(request.form['command'], request.form.get('arg1'), request.form.get('arg2'), request.form.get('arg3'), request)
                else:
                    return ins_page.process_ajax(command, request)
            P.logger.error(f"not process ajax : {P.package_name} {module_name} {page_name} {command}")
        except Exception as exception: 
            P.logger.error('Exception:%s', exception)
            P.logger.error(traceback.format_exc())

    #########################################################
    # API - 외부
    #########################################################
    # 단일 모듈인 경우 모듈이름을 붙이기 불편하여 추가.
    @P.blueprint.route('/api/<sub2>', methods=['GET', 'POST'])
    @F.check_api
    def api_first(sub2):
        try:
            for module in P.module_list:
                return module.process_api(sub2, request)
        except Exception as exception: 
            P.logger.error('Exception:%s', exception)
            P.logger.error(traceback.format_exc())

    @P.blueprint.route('/api/<sub>/<sub2>', methods=['GET', 'POST'])
    @F.check_api
    def api(sub, sub2):
        try:
            for module in P.module_list:
                if sub == module.name:
                    return module.process_api(sub2, request)
        except Exception as exception: 
            P.logger.error('Exception:%s', exception)
            P.logger.error(traceback.format_exc())

    @P.blueprint.route('/normal/<sub>/<sub2>', methods=['GET', 'POST'])
    def normal(sub, sub2):
        try:
            for module in P.module_list:
                if sub == module.name:
                    return module.process_normal(sub2, request)
        except Exception as exception: 
            P.logger.error('Exception:%s', exception)
            P.logger.error(traceback.format_exc())






























def default_route_single_module(P):
    @P.blueprint.route('/')
    def home():
        return redirect('/{package_name}/{home_module}'.format(package_name=P.package_name, home_module=P.home_module))
        
    @P.blueprint.route('/<sub>', methods=['GET', 'POST'])
    @login_required
    def first_menu(sub):
        if sub == 'log':
            return render_template('log.html', package=P.package_name)
        return P.module_list[0].process_menu(sub, request)

    @P.blueprint.route('/ajax/<sub>', methods=['GET', 'POST'])
    @login_required
    def ajax(sub):
        P.logger.debug('AJAX %s %s', P.package_name, sub)
        try:
            # global
            if sub == 'setting_save':
                ret, change_list = P.ModelSetting.setting_save(request)
                if ret:
                    P.module_list[0].setting_save_after(change_list)
                    if P.module_list[0].page_list is not None:
                        for page_ins in P.module_list[0].page_list:
                            page_ins.setting_save_after(change_list)
                return jsonify(ret)
            elif sub == 'scheduler':
                sub = request.form['sub']
                go = request.form['scheduler']
                P.logger.debug('scheduler :%s', go)
                if go == 'true':
                    P.logic.scheduler_start(sub)
                else:
                    P.logic.scheduler_stop(sub)
                return jsonify(go)
            elif sub == 'reset_db':
                sub = request.form['sub']
                ret = P.logic.reset_db(sub)
                return jsonify(ret)
            elif sub == 'one_execute':
                sub = request.form['sub']
                ret = P.logic.one_execute(sub)
                return jsonify(ret)
            else:
                return P.module_list[0].process_ajax(sub, request)
        except Exception as exception: 
            P.logger.error('Exception:%s', exception)
            P.logger.error(traceback.format_exc())  

    @P.blueprint.route('/api/<sub>', methods=['GET', 'POST'])
    @F.check_api
    def api(sub):
        try:
            return P.module_list[0].process_api(sub, request)
        except Exception as exception: 
            P.logger.error('Exception:%s', exception)
            P.logger.error(traceback.format_exc())

    @P.blueprint.route('/normal/<sub>', methods=['GET', 'POST'])
    def normal(sub):
        try:
            return P.module_list[0].process_normal(sub, request)
        except Exception as exception: 
            P.logger.error('Exception:%s', exception)
            P.logger.error(traceback.format_exc())    


























def default_route_socketio_module(module):
    P = module.P
    if module.socketio_list is None:
        module.socketio_list = []

    @F.socketio.on('connect', namespace=f'/{P.package_name}/{module.name}')
    def connect():
        try:
            P.logger.debug(f'socket_connect : {P.package_name} - {module.name}')
            module.socketio_list.append(request.sid)
            socketio_callback('start', '')
            module.socketio_connect()
        except Exception as exception: 
            P.logger.error('Exception:%s', exception)
            P.logger.error(traceback.format_exc())


    @F.socketio.on('disconnect', namespace='/{package_name}/{sub}'.format(package_name=P.package_name, sub=module.name))
    def disconnect():
        try:
            P.logger.debug('socket_disconnect : %s - %s', P.package_name, module.name)
            module.socketio_list.remove(request.sid)
            module.socketio_disconnect()
        except Exception as exception: 
            P.logger.error('Exception:%s', exception)
            P.logger.error(traceback.format_exc())


    def socketio_callback(cmd, data, encoding=True):
        if module.socketio_list:
            if encoding:
                data = json.dumps(data, cls=AlchemyEncoder)
                data = json.loads(data)
            F.socketio.emit(cmd, data, namespace='/{package_name}/{sub}'.format(package_name=P.package_name, sub=module.name), broadcast=True)

    module.socketio_callback = socketio_callback
























def default_route_socketio_page(page):
    
    module = page.parent
    P = page.P
    if page.socketio_list is None:
        page.socketio_list = []

    @F.socketio.on('connect', namespace=f'/{P.package_name}/{module.name}/{page.name}')
    def page_socketio_connect():
        try:
            P.logger.debug(f'socket_connect : {P.package_name}/{module.name}/{page.name}')
            page.socketio_list.append(request.sid)
            page_socketio_socketio_callback('start', '')
        except Exception as e: 
            P.logger.error(f'Exception:{str(e)}')
            P.logger.error(traceback.format_exc())


    @F.socketio.on('disconnect', namespace=f'/{P.package_name}/{module.name}/{page.name}')
    def page_socketio_disconnect():
        try:
            P.logger.debug(f'socket_disconnect : {P.package_name}/{module.name}/{page.name}')
            page.socketio_list.remove(request.sid)
        except Exception as e: 
            P.logger.error(f'Exception:{str(e)}')
            P.logger.error(traceback.format_exc())


    def page_socketio_socketio_callback(cmd, data, encoding=True):
        if page.socketio_list:
            if encoding:
                data = json.dumps(data, cls=AlchemyEncoder)
                data = json.loads(data)
            F.socketio.emit(cmd, data, namespace=f'/{P.package_name}/{module.name}/{page.name}', broadcast=True)

    page.socketio_callback = page_socketio_socketio_callback
