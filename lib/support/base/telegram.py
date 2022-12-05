import time
import traceback

import requests
from telepot_mod import Bot

from . import logger


class SupportTelegram:

    @classmethod
    def send_telegram_message(cls, text, bot_token=None, chat_id=None, image_url=None,  disable_notification=None):
        try:
            bot = Bot(bot_token)
            if image_url is not None:
                logger.debug(image_url)
                for i in range(5):
                    if requests.get(image_url).status_code == 200:
                        break
                    else:
                        time.sleep(3)
                try:
                    bot.sendPhoto(chat_id, image_url, disable_notification=disable_notification)
                except Exception as e: 
                    logger.error(f"Exception:{str(e)}")
                    logger.error(traceback.format_exc()) 
            bot.sendMessage(chat_id, text, disable_web_page_preview=True, disable_notification=disable_notification)
            return True
        except Exception as e: 
            logger.error(f"Exception:{str(e)}")
            logger.error(traceback.format_exc()) 
            logger.debug('Chatid:%s', chat_id)
        return False
