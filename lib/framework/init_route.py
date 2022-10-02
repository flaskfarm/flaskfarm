# -*- coding: utf-8 -*-
#########################################################
# python
import os
import sys
from datetime  import datetime, timedelta
import json
import traceback

# third-party
from flask import redirect, render_template, Response, request, jsonify, send_from_directory
from flask_login import login_user, logout_user, current_user, login_required

# sjva 공용
from framework import F, check_api, app, db, VERSION, logger, path_data
import system



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
            return jsonify(True)



@app.route('/robots.txt')
def robot_to_root():
    return send_from_directory('', 'static/file/robots.txt')






















@app.route("/")
@app.route("/None")
@app.route("/home")
def home():
    return redirect('/system/home')


@app.route("/version")
def get_version():
    return VERSION

@app.route("/open/<path:path>")
@login_required
def open_file(path):
    return send_from_directory('/', path)


@app.route("/file/<path:path>")
@check_api
def file2(path):
    logger.debug('file2 :%s', path)
    return send_from_directory('/', path)




@app.route("/up", methods=['GET', 'POST'])
def upload():
    # curl -F file=@downloader_video.tar https://dev.soju6jan.com/up
    # 
    try:
        if request.method == 'POST':
            f = request.files['file']
            from werkzeug import secure_filename
            tmp = secure_filename(f.filename)
            logger.debug('upload : %s', tmp)
            f.save(os.path.join(path_data, 'upload', tmp))
            return jsonify('success')
    except Exception as exception:
        logger.error('Exception:%s', exception)
        logger.error(traceback.format_exc())
        return jsonify('fail')

