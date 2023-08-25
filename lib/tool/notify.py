import traceback
from datetime import datetime

from framework import F
from support import SupportDiscord, SupportTelegram, SupportYaml, SupportSlack

from . import logger


class ToolNotify(object):

    @classmethod 
    def send_message(cls, text, message_id=None, image_url=None):
        if F.SystemModelSetting.get_bool('notify_advaned_use'):
            return cls.send_advanced_message(text, image_url=image_url, message_id=message_id)
        else:
            if F.SystemModelSetting.get_bool('notify_telegram_use'):
                SupportTelegram.send_telegram_message(text, image_url=image_url, bot_token=F.SystemModelSetting.get('notify_telegram_token'), chat_id=F.SystemModelSetting.get('notify_telegram_chat_id'))
            if F.SystemModelSetting.get_bool('notify_discord_use'):
                SupportDiscord.send_discord_message(text, image_url=image_url, webhook_url=F.SystemModelSetting.get('notify_discord_webhook')) 
            if F.SystemModelSetting.get_bool('notify_slack_use'):
                SupportSlack.send_slack_message(text, image_url=image_url, webhook_url=F.SystemModelSetting.get('notify_slack_webhook'))


    @classmethod
    def send_advanced_message(cls, text, image_url=None, policy=None, message_id=None): 
        try:
            message_id = message_id.strip()
            policy = SupportYaml.read_yaml(F.config['notify_yaml_filepath'])
            if message_id is None or message_id not in policy:
                message_id = 'DEFAULT'
            now = datetime.now()
            for item in policy[message_id]:
                if item.get('enable_time') != None:
                    tmp = item.get('enable_time').split('-')
                    if now.hour < int(tmp[0]) or now.hour > int(tmp[1]):
                        continue
                if item.get('type') == 'telegram':
                    if item.get('token', '') == '' or item.get('chat_id', '') == '':
                        continue
                    SupportTelegram.send_telegram_message(text, image_url=image_url, bot_token=item.get('token'), chat_id=item.get('chat_id'), disable_notification=item.get('disable_notification', False))
                elif item.get('type') == 'discord':
                    if item.get('webhook', '') == '':
                        continue
                    SupportDiscord.send_discord_message(text, image_url=image_url, webhook_url=item.get('webhook'))
                elif item.get('type') == 'slack':
                    if item.get('webhook', '') == '':
                        continue
                    SupportSlack.send_slack_message(text, image_url=image_url, webhook_url=item.get('webhook'))
            return True
        except Exception as e: 
            logger.error(f"Exception:{str(e)}")
            logger.error(traceback.format_exc()) 
        return False
