import os
import threading
import time
import traceback

from framework import F
from support import SupportSubprocess


class ToolModalCommand(object):
    __thread = None
    __title = None
    __commands = None
    __clear = None
    __show_modal = None
    __wait = None
    __ss_process = None
    __abort = None


    @classmethod
    def start(cls, title, commands, clear=True, wait=False, show_modal=True):
        if cls.__thread != None:
            cls.__abort = True
            cls.__thread = None
        if cls.__ss_process != None:
            cls.__ss_process.process_close()
            cls.__ss_process = None
        cls.__title = title
        cls.__commands = commands
        cls.__clear = clear
        cls.__wait = wait
        cls.__show_modal = show_modal
        cls.__thread = None
        cls.__abort = False
        cls.__start()


    @classmethod
    def __start(cls):
        try:
            if cls.__show_modal:
                if cls.__clear:
                    F.socketio.emit("command_modal_clear", None, namespace='/framework', broadcast=True)
            cls.__thread = threading.Thread(target=cls.__execute_thread_function, args=())
            cls.__thread.setDaemon(True)
            cls.__thread.start()
            if cls.__wait:
                time.sleep(1)
                cls.__thread.join()
        except Exception as exception: 
            F.logger.error('Exception:%s', exception)
            F.logger.error(traceback.format_exc())

    @classmethod
    def __execute_thread_function(cls):
        try:
            if cls.__show_modal:
                F.socketio.emit("command_modal_show", cls.__title, namespace='/framework', broadcast=True)
                F.socketio.emit("loading_hide", None, namespace='/framework', broadcast=True)
                
            for command in cls.__commands:
                if cls.__abort:
                    return
                if command[0] == 'msg':
                    if cls.__show_modal:
                        F.socketio.emit("command_modal_add_text", '%s\n\n' % command[1], namespace='/framework', broadcast=True)
                elif command[0] == 'system':
                    if cls.__show_modal:
                        F.socketio.emit("command_modal_add_text", '$ %s\n\n' % command[1], namespace='/framework', broadcast=True)
                    os.system(command[1])
                else:
                    #show_command = True
                    #if command[0] == 'hide':
                    #    show_command = False
                    #    command = command[1:]
                    cls.__ss_process = SupportSubprocess(command, stdout_callback=cls.process_callback, callback_line=False)
                    cls.__ss_process.start()
                    cls.__ss_process.process_close()
                    cls.__ss_process = None
                time.sleep(1)
        except Exception as exception: 
            if cls.__show_modal:
                F.socketio.emit("command_modal_show", cls.__title, namespace='/framework', broadcast=True)
                F.socketio.emit("command_modal_add_text", str(exception), namespace='/framework', broadcast=True)
                F.socketio.emit("command_modal_add_text", str(traceback.format_exc()), namespace='/framework', broadcast=True)

    @classmethod
    def process_callback(cls, call_id, mode, text):
        #F.logger.warning(text)
        if cls.__show_modal == False:
            return
        if mode == 'end':
            F.socketio.emit("command_modal_add_text", "\n\n<<프로세스 종료>>", namespace='/framework', broadcast=True)
            F.socketio.emit("command_modal_input_disable", "", namespace='/framework', broadcast=True)
        elif mode == 'thread_end':
            #F.socketio.emit("command_modal_add_text", "\n\n<<프로세스 종료>>", namespace='/framework', broadcast=True)
            F.socketio.emit("command_modal_input_disable", "", namespace='/framework', broadcast=True)
        else:
            F.socketio.emit("command_modal_add_text", text, namespace='/framework', broadcast=True)

    
    @classmethod
    def modal_close(cls):
        if cls.__thread != None:
            cls.__abort = True
            
        if cls.__ss_process != None:
            cls.__ss_process.process_close()
            cls.__ss_process = None

    @classmethod
    def input_command(cls, cmd):
        if cls.__ss_process != None:
            cls.__ss_process.input_command(cmd)


    @classmethod
    def send_message(cls, text):
        F.socketio.emit("command_modal_add_text", '%s\n\n' % text, namespace='/framework', broadcast=True)
