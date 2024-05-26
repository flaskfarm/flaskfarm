import os
import traceback

try:
    from slack_sdk.webhook import WebhookClient
except:
    os.system('pip3 install slack-sdk')
    from slack_sdk.webhook import WebhookClient
from . import logger

class SupportSlack:
    @classmethod
    def send_slack_message(cls, text, webhook_url=None, image_url=None, disable_notification=None):
        try:
            if webhook_url is None:
                return False
            webhook = WebhookClient(webhook_url)
            if image_url is not None:
                webhook.send(text=text, blocks=[{"type": "image", "title": {"type": "plain_text", "text": "Image", "emoji": True}, "image_url": image_url, "alt_text": "Image"}])
            webhook.send(text=text)
            return True
        except Exception as e:
            logger.error(f"Exception:{str(e)}")
            logger.error(traceback.format_exc())
        return False