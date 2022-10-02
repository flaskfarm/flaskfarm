import json
import os
import sys
import traceback
from datetime import datetime, timedelta

import system
from flask import (Response, jsonify, redirect, render_template, request,
                   send_from_directory)
from flask_login import current_user, login_required, login_user, logout_user

# sjva 공용
from framework import VERSION, F 


@F.app.route('/global/ajax/<sub>', methods=['GET', 'POST'])
@login_required
def global_ajax(sub):
    #logger.debug('/global/ajax/%s', sub)
    if sub == 'listdir':
        if 'path' in request.form:
            #if os.path.isfile(request.form['path']):
            #    return jsonify('')
            path = request.form['path']
            if os.path.isfile(path):
                path = os.path.dirname(path)
            result_list = os.listdir(path)

            if 'only_dir' in request.form and request.form['only_dir'].lower() == 'true':
                result_list = [name for name in result_list if os.path.isdir(os.path.join(path, name))]

            result_list.sort()
            result_list = [f"{x}|{os.path.join(path,x)}" for x in result_list]
            tmp = os.path.dirname(path)
            if path != tmp:
                result_list = [f'..|{tmp}'] + result_list
            return jsonify(result_list)
        else:
            return jsonify(None)    
    elif sub == 'is_available_edit':
        # globalEditBtn
        try:
            import flaskcode
            return jsonify(True)
        except:
            return jsonify(False)



@F.app.route('/robots.txt')
def robot_to_root():
    return send_from_directory('', 'static/file/robots.txt')






















@F.app.route("/")
@F.app.route("/None")
@F.app.route("/home")
def home():
    return redirect('/system/home')


@F.app.route("/version")
def get_version():
    return VERSION

@F.app.route("/open/<path:path>")
@login_required
def open_file(path):
    return send_from_directory('/', path)


@F.app.route("/file/<path:path>")
@F.check_api
def file2(path):
    F.logger.debug('file2 :%s', path)
    return send_from_directory('/', path)




@F.app.route("/up", methods=['GET', 'POST'])
def upload():
    # curl -F file=@downloader_video.tar https://dev.soju6jan.com/up
    # 
    try:
        if request.method == 'POST':
            f = request.files['file']
            from werkzeug import secure_filename
            tmp = secure_filename(f.filename)
            F.logger.debug('upload : %s', tmp)
            f.save(os.path.join(F.path_data, 'upload', tmp))
            return jsonify('success')
    except Exception as exception:
        F.logger.error('Exception:%s', exception)
        F.logger.error(traceback.format_exc())
        return jsonify('fail')

