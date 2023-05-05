from flask_login import current_user, login_user, logout_user

from .setup import *

name = 'route'

class ModuleRoute(PluginModuleBase):
    def __init__(self, P):
        super(ModuleRoute, self).__init__(P, name=name)
        self.route()

    # 일반적인 routing에서는 login_required 때문에 /system/login으로 redirect 됨.
    def route(self):
        @P.blueprint.route('/login', methods=['GET', 'POST'])
        def login():
            if F.SystemModelSetting.get_bool('use_login') == False:
                username = F.SystemModelSetting.get('web_id')
                F.users[username].authenticated = True
                login_user(frame.users[username], remember=True)
                #current_user = USERS[username]
                return redirect(request.args.get("next"))
            return render_template(f'system_login.html', next=request.args.get("next"))

        @P.blueprint.route('/ajax/login/<cmd>', methods=['POST'])
        def command(cmd):
            if cmd == 'command':
                return self.process_command(request.form['command'], request.form.get('arg1'), request.form.get('arg2'), request.form.get('arg3'), request)

        @P.blueprint.route('/logout', methods=['GET'])
        def logout():
            current_user.authenticated = False
            logout_user()
            return redirect('/')

        @F.login_manager.user_loader
        def user_loader(user_id):
            return F.users[user_id]


        @P.blueprint.route('/restart', methods=['GET'])
        @login_required
        def restart():
            threading.Timer(1, F.restart).start()
            return render_template('system_restart.html',sub='restart', referer=request.headers.get("Referer"))
        

        @P.blueprint.route('/shutdown', methods=['GET'])
        @login_required
        def shutdown():
            threading.Timer(1, F.shutdown).start()
            return render_template('system_restart.html',sub='shutdown', referer=request.headers.get("Referer"))


        @F.socketio.on('connect', namespace=f'/{P.package_name}/restart')
        def restart_socket_connect():
            F.socketio.emit('connect', {}, namespace='/{P.package_name}/restart')


    def process_menu(self, page, req):
        return render_template('sample.html', title=f"{__package__}/{name}/{page}")
        #return render_template(f'{__package__}_{name}.html', arg={})

    def process_command(self, command, arg1, arg2, arg3, req):
        if command == 'login':
            username = arg1
            password = arg2
            remember = (arg3 == 'true')
            if username not in frame.users:
                return jsonify('no_id')
            elif not F.users[username].can_login(password):
                return jsonify('wrong_password')
            else:
                F.users[username].authenticated = True
                login_user(frame.users[username], remember=remember)
                return jsonify('redirect')
            