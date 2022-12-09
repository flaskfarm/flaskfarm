import os

from support import d, logger

try:
    from selenium import webdriver
except:
    os.system("pip install --upgrade selenium")
    from selenium import webdriver

import base64
import threading
import time
import traceback

from selenium import webdriver
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


class SupportSimpleSelenium(object):
    
    def __init__(self, P, mode="local", headless=False, remote=None):
        self.P = P
        self.driver = None
        self.timeout = 5
        self.driver_init(mode=mode, headless=headless, remote=remote)


    def driver_init(self, mode='local', headless=False, remote=None):
        if mode == 'local':
            from selenium.webdriver.chrome.options import Options
            options = Options()
            if headless:
                options.add_argument('headless')
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        elif mode == 'remote':
            from selenium.webdriver.chrome.options import Options
            options = Options()
            #options.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36")
            #options.set_preference("general.platform.override", "Win32")
            self.driver = webdriver.Remote(remote, options=options)


    def get_pagesoruce(self, url, wait_xpath="/html/body", retry=True):
        try:
            self.driver.get(url)
            WebDriverWait(self.driver, self.timeout).until(lambda driver: driver.find_element(By.XPATH, wait_xpath))
            return self.driver.page_source
        except Exception as e: 
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc()) 
            self.driver_quit()
            if retry:
                return self.get_pagesoruce(url, wait_xpath=wait_xpath, retry=False)


    def driver_quit(self):
        if self.driver != None:
            def func():
                self.driver.quit()
                self.driver = None
                #self.logger.debug('driver quit..')
            th = threading.Thread(target=func, args=())
            th.setDaemon(True)
            th.start()
    
    def get_downloaded_files(self):
        if not self.driver.current_url.startswith("chrome://downloads"):
            self.driver.get("chrome://downloads/")
        #driver.implicitly_wait(4)
        self.driver.implicitly_wait(2)
        return self.driver.execute_script( \
            "return  document.querySelector('downloads-manager')  "
            " .shadowRoot.querySelector('#downloadsList')         "
            " .items.filter(e => e.state === 'COMPLETE')          "
            " .map(e => e.filePath || e.file_path || e.fileUrl || e.file_url); ")
    


    def get_file_content(self, path):
        elem = self.driver.execute_script( \
            "var input = window.document.createElement('INPUT'); "
            "input.setAttribute('type', 'file'); "
            "input.hidden = true; "
            "input.onchange = function (e) { e.stopPropagation() }; "
            "return window.document.documentElement.appendChild(input); " )

        elem._execute('sendKeysToElement', {'value': [ path ], 'text': path})

        result = self.driver.execute_async_script( \
            "var input = arguments[0], callback = arguments[1]; "
            "var reader = new FileReader(); "
            "reader.onload = function (ev) { callback(reader.result) }; "
            "reader.onerror = function (ex) { callback(ex.message) }; "
            "reader.readAsDataURL(input.files[0]); "
            "input.remove(); "
            , elem)

        if not result.startswith('data:') :
            raise Exception("Failed to get file content: %s" % result)

        return base64.b64decode(result[result.find('base64,') + 7:])
    

    


    

    # docker run -d --name selenium_chromium -it -p 4446:4444 -p 5902:5900 -p 7902:7900 --shm-size 2g seleniarm/standalone-chromium:latest