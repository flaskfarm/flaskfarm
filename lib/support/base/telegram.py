import traceback

from telepot_mod import Bot

from . import logger


class SupportTelegram:

    @classmethod
    def send_telegram_message(cls, text, bot_token=None, chat_id=None, image_url=None,  disable_notification=None):
        try:
            bot = Bot(bot_token)
            if image_url is not None:
                bot.sendPhoto(chat_id, image_url, disable_notification=disable_notification)
            bot.sendMessage(chat_id, text, disable_web_page_preview=True, disable_notification=disable_notification)
            return True
        except Exception as exception: 
            logger.error('Exception:%s', exception)
            logger.error(traceback.format_exc()) 
            logger.debug('Chatid:%s', chat_id)
        return False
