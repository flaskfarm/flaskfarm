import os
import random
import time
import traceback

import requests

try:
    from discord_webhook import DiscordEmbed, DiscordWebhook
except:
    os.system('pip3 install discord-webhook')

# 2023-10-13 by flaskfarm
# 웹훅 URL이 git에 노출되면 중단.
# base64로 인코딩.
import base64

from discord_webhook import DiscordEmbed, DiscordWebhook

from . import logger

webhook_list = [
    base64.b64decode(b'aHR0cHM6Ly9kaXNjb3JkLmNvbS9hcGkvd2ViaG9va3MvMTE2MjIyODM4MzE4MzI4MjIyNy9ORXpNWFBmT05vbUU3bl8xck1iT0ZWQUI4ZmlXN21vRFlGYnJHRk03UlJSWF90ZGMyS0lxY2hWcXV6VF8wVm5ZUEJRVQ==').decode('utf-8'), # 1
    base64.b64decode(b'aHR0cHM6Ly9kaXNjb3JkLmNvbS9hcGkvd2ViaG9va3MvMTE2MjIyODc5MzExMzU4MzY3Ni94dEZlWnRWbkhEUGc4aFBYZkZDMkFidUtDSmlwNjQ0d1RQMDFJalVncTR5ODB6XzZCRi1kTFctemlEdGNlWF84RXVtRw==').decode('utf-8'), # 2
    base64.b64decode(b'aHR0cHM6Ly9kaXNjb3JkLmNvbS9hcGkvd2ViaG9va3MvMTE2MjIyODkyMTA4MTgxMDk1NS9xOUVYZndHYll6bHdwM1MtMnpxUmxZcnJYWS1nTUttTTRlTUd0YW8zNTF1d1c2N0U2ckNFUW0zWDJhbDJURnFXMHR4cw==').decode('utf-8'), # 3
    base64.b64decode(b'aHR0cHM6Ly9kaXNjb3JkLmNvbS9hcGkvd2ViaG9va3MvMTE2MjIyOTA4MzA0NDg1MTc3My9jVU1YRkVERHQ2emtWOW90Mmd5dlpYeVlOZV9VcGtmcmZhTzg5aHZoLVdod0c0Z24zOGJhT19DVkg2Z0N4clFraVZRcA==').decode('utf-8'), # 4
    base64.b64decode(b'aHR0cHM6Ly9kaXNjb3JkLmNvbS9hcGkvd2ViaG9va3MvMTE2MjIyOTE4MzAwMzQ5MjM5Mi9CVXl1U3lKTHc1cktHdFRKOWhqRDk3SklKWW9HSTZ6SnJ4MzdLX0s4TkVKU3ZTYlZ4aC0tMVFRMEFZbTJFa0tzaEJRcQ==').decode('utf-8'), # 5
    base64.b64decode(b'aHR0cHM6Ly9kaXNjb3JkLmNvbS9hcGkvd2ViaG9va3MvMTE2MjIyOTI4OTQ4ODQ5NDY0My9XLWhZck95QTBza2M1dUdVTkpyenU4ZHFSMVF0QmMtOVAzMW45RHhQWkhVLXptdEZ3MWVLWTE0dlZubkRUV25EU2ZRTw==').decode('utf-8'), # 6
    base64.b64decode(b'aHR0cHM6Ly9kaXNjb3JkLmNvbS9hcGkvd2ViaG9va3MvMTE2MjIyOTQwOTExODQzNzQ2OS95NDRjVTkwM1hLS2NyaWFidERHMzRuMzZfRkZsMF9TV2p4b0lWMlBZY0dxNWxyU1dxVWt5ZklkZlcwM0FFVDJObThMaQ==').decode('utf-8'), # 7
    base64.b64decode(b'aHR0cHM6Ly9kaXNjb3JkLmNvbS9hcGkvd2ViaG9va3MvMTE2MjIyOTQ5NTQyNDYxODQ5Ni9PSnFlVHRhZ1FtVGFrU2VNQkRucVhZRTJieWRuX2cweHV2VTA0WmdKS3NjWEQydkVHbHBWYzdhQWZMQ0ZYSXNTbTN5OQ==').decode('utf-8'), # 8
    base64.b64decode(b'aHR0cHM6Ly9kaXNjb3JkLmNvbS9hcGkvd2ViaG9va3MvMTE2MjIyOTU4NzE2NjY0MjM2OC9PeG9NRllUT1dOWmcwS3pfQ3k2ZXowX2laQnpqbm02QVkyTjJfMWhaVHhYdWxPRm5oZ0lsOGxxcUVYNVVWRWhyMHJNcw==').decode('utf-8'), # 9
    base64.b64decode(b'aHR0cHM6Ly9kaXNjb3JkLmNvbS9hcGkvd2ViaG9va3MvMTE2MjIyOTY4OTM3NzYzNjQ3Mi9iblgyYTNsWjI1R2NZZ1g4Sy1JeXZVcS1TMV9zYmhkbEtoSTI4eWp6SWdHOHRyekFWMXBKUkgxYkdrdmhzMVNUNS1uMg==').decode('utf-8'), # 10
    base64.b64decode(b'aHR0cHM6Ly9kaXNjb3JkLmNvbS9hcGkvd2ViaG9va3MvMTE2MjIyOTgwMTg0MzY5MTY4Mi96OUFocjZjNmxaS1VyWV9TRmhfODVQeEVlSjJuQW8wMXlHS3RCUWpNNnJmR3JGVXdvQ1oyQ3NJYmlTMHQ1NDZwU3NUUg==').decode('utf-8'), # 11
    base64.b64decode(b'aHR0cHM6Ly9kaXNjb3JkLmNvbS9hcGkvd2ViaG9va3MvMTE2MjIyOTk0NjQyMTM2Njg0NC9BYnFVRlJCN0dzb3ktUkdfMzBLNXZkNm9XUWRnbkpDZ1ctTlpBbkFRN0N2TzdsNjRfeXRkY0ZHUkhLV2RldE1jQzhTSw==').decode('utf-8'), # 12
    base64.b64decode(b'aHR0cHM6Ly9kaXNjb3JkLmNvbS9hcGkvd2ViaG9va3MvMTE2MjIzMDExNjAyNjQyMTM0OC82dG1NOTA2eV9QTHJ3WGFxcGNZS25OMEJIQjlDTkxJT1dJeTdpc3Exbm9VMHJxU2V0NzI2R1Y4Zk9Ua2pCbDZacXMxVA==').decode('utf-8'), # 13
    base64.b64decode(b'aHR0cHM6Ly9kaXNjb3JkLmNvbS9hcGkvd2ViaG9va3MvMTE2MjIzMDIwMTExMjA3MjM2My9DYkdkcVdvd3hCcTV3ck1hck0taGZqajVIbFJ2VFFWa0tuZUVaVl9yMlc1UkxHZFZpWW15VzZZcl9PbEJCZG5KWk1wNw==').decode('utf-8'), # 14
    base64.b64decode(b'aHR0cHM6Ly9kaXNjb3JkLmNvbS9hcGkvd2ViaG9va3MvMTE2MjIzMDI5MTUwNzcyNDQwOC9UanJFc08zSTJyT3l0d0ZvVFhUSlNTOXphaDJpbG9CcVk3TzhHMHZWbDROTmI0aGpaaDNjVGo0cGNla2lxa3RqaGRPTg==').decode('utf-8'), # 15
    base64.b64decode(b'aHR0cHM6Ly9kaXNjb3JkLmNvbS9hcGkvd2ViaG9va3MvMTE2MjIzMDM3NDQ4NzgzNDc3NC85ZFpodjZfajRuT0hpbGtMaFVVc1B6OVFKa2dqQ3BJZ19PWE55YnZtV1BiQlNVdmRZWC1IVW5UM3RneDlKdnZlYjVMZw==').decode('utf-8'), # 16
    base64.b64decode(b'aHR0cHM6Ly9kaXNjb3JkLmNvbS9hcGkvd2ViaG9va3MvMTE2MjIzMDU2ODkzMTU2OTc3NC82MTFBVTg0ZUZBcXllWlktQ2lPbnozbm4zSHg3ZldwQUNCbjlMTFNENUFJdHRkYjVHSm9pV3B1dHpxdEVHZ3l0RHlXYg==').decode('utf-8'), # 17
    base64.b64decode(b'aHR0cHM6Ly9kaXNjb3JkLmNvbS9hcGkvd2ViaG9va3MvMTE2MjIzMDY3MzkxMDgwMDM4Ni9jbEZvZHEwREhGNUlvYUtVRXVRcXNGbnB3OXZoZUx1RU1qbVJFNjQyRUZGa21wYXBwMzhYWDNPMmZKWUVSdjMzY0tORg==').decode('utf-8'), # 18
    base64.b64decode(b'aHR0cHM6Ly9kaXNjb3JkLmNvbS9hcGkvd2ViaG9va3MvMTE2MjIzMDc0OTMyMDE5NjE5OC8weE1vZ2o5UXRCM1NGZE5KYk04STk1LU9XQzI2Zm1WTWpjelpSX2REY2hnblZoUk1QelVzRHFlYTc0QUdISFRFVWFVZQ==').decode('utf-8'), # 19
    base64.b64decode(b'aHR0cHM6Ly9kaXNjb3JkLmNvbS9hcGkvd2ViaG9va3MvMTE2MjIzMDg0NTMxNTIyMzU2Mi9HWVItZUo2WFltdy1VMHRkWWY5QXdnU2JVZFpSb1k4aWx2MlVxaVJBSnlBdDBsYWV5ck1tSzJmRGp5T1YyenBJUUR2bA==').decode('utf-8'), # 20
]


class SupportDiscord(object):

    @classmethod
    def send_discord_message(cls, text, image_url=None, webhook_url=None):
        try:
            """
            webhook = DiscordWebhook(url=webhook_url, content=text)
            if image_url is not None:
                embed = DiscordEmbed()
                embed.set_timestamp()
                embed.set_image(url=image_url)
                webhook.add_embed(embed)
            """
            try:
                
                if image_url is not None:
                    webhook = DiscordWebhook(url=webhook_url)
                    embed = DiscordEmbed()
                    embed.set_timestamp()
                    embed.set_image(url=image_url)
                    tmp = text.split('\n', 1)
                    embed.set_title(tmp[0])
                    embed.set_description(tmp[1])
                    webhook.add_embed(embed)
                else:
                    if 'http://' in text or 'https://' in text:
                        webhook = DiscordWebhook(url=webhook_url, content= text)
                    else:
                        webhook = DiscordWebhook(url=webhook_url, content='```' + text + '```')
                webhook.execute()
                return True
            except:
                webhook = DiscordWebhook(url=webhook_url, content=text)
                if image_url is not None:
                    embed = DiscordEmbed()
                    embed.set_timestamp()
                    embed.set_image(url=image_url)
                    webhook.add_embed(embed)
                webhook.execute()
                return True
        except Exception as e: 
            logger.error(f"Exception:{str(e)}")
            logger.error(traceback.format_exc()) 
        return False


    @classmethod
    def send_discord_bot_message(cls, text, webhook_url, encryped=True):
        try:
            from support import SupportAES
            if encryped:
                text = '^' + SupportAES.encrypt(text)
            return cls.send_discord_message(text, webhook_url=webhook_url)
        except Exception as e: 
            logger.error(f"Exception:{str(e)}")
            logger.error(traceback.format_exc()) 
            return False


    
    @classmethod
    def discord_proxy_image(cls, image_url, webhook_url=None, retry=True):
        #2020-12-23
        #image_url = None
        if image_url == '' or image_url is None:
            return
        data = None
        
        if webhook_url is None or webhook_url == '':
            webhook_url =  webhook_list[random.randint(0,len(webhook_list)-1)]

        try:
            webhook = DiscordWebhook(url=webhook_url, content='')
            embed = DiscordEmbed()
            embed.set_timestamp()
            embed.set_image(url=image_url)
            webhook.add_embed(embed)
            import io
            byteio = io.BytesIO()
            webhook.add_file(file=byteio.getvalue(), filename='dummy')
            response = webhook.execute()
            data = None
            if type(response) == type([]):
                if len(response) > 0:
                    data = response[0].json()
            else:
                data = response.json()    
            
            if data is not None and 'embeds' in data:
                target = data['embeds'][0]['image']['proxy_url']
                if requests.get(target).status_code == 200:
                    return target
                else:
                    return image_url
            else:
                raise Exception(str(data))
        except Exception as e: 
            logger.error(f"Exception:{str(e)}")
            logger.error(traceback.format_exc())
            if retry:
                time.sleep(1)
                return cls.discord_proxy_image(image_url, webhook_url=None, retry=False)
            else:
                return image_url

    
    @classmethod
    def discord_proxy_image_localfile(cls, filepath, retry=True):
        data = None
        webhook_url =  webhook_list[random.randint(0,len(webhook_list)-1)]

        try:
            webhook = DiscordWebhook(url=webhook_url, content='')
            import io
            with open(filepath, 'rb') as fh:
                byteio = io.BytesIO(fh.read())
            webhook.add_file(file=byteio.getvalue(), filename='image.jpg')
            embed = DiscordEmbed()
            embed.set_image(url="attachment://image.jpg")
            response = webhook.execute()
            data = None
            if type(response) == type([]):
                if len(response) > 0:
                    data = response[0].json()
            else:
                data = response.json()    
            
            if data is not None and 'attachments' in data:
                target = data['attachments'][0]['url']
                if requests.get(target).status_code == 200:
                    return target
            if retry:
                time.sleep(1)
                return cls.discord_proxy_image_localfile(filepath, retry=False)
        except Exception as e: 
            logger.error(f"Exception:{str(e)}")
            logger.error(traceback.format_exc())
    
            if retry:
                time.sleep(1)
                return cls.discord_proxy_image_localfile(filepath, retry=False)


    @classmethod
    def discord_proxy_image_bytes(cls, bytes, retry=True, format='jpg'):
        data = None
        idx = random.randint(0,len(webhook_list)-1)
        webhook_url =  webhook_list[idx]
        try:
            webhook = DiscordWebhook(url=webhook_url, content='')
            webhook.add_file(file=bytes, filename=f'image.{format}')
            embed = DiscordEmbed()
            embed.set_image(url=f"attachment://image.{format}")
            response = webhook.execute()
            data = None
            if type(response) == type([]):
                if len(response) > 0:
                    data = response[0].json()
            else:
                data = response.json()    
            if data is not None and 'attachments' in data:
                target = data['attachments'][0]['url']
                if requests.get(target).status_code == 200:
                    return target
            logger.error(f"discord webhook error : {webhook_url}")
            logger.error(f"discord webhook error : {idx}")
            if retry:
                time.sleep(1)
                return cls.discord_proxy_image_bytes(bytes, retry=False)
        except Exception as e: 
            logger.error(f"Exception:{str(e)}")
            logger.error(traceback.format_exc())

            if retry:
                time.sleep(1)
                return cls.discord_proxy_image_bytes(bytes, retry=False)




    # RSS에서 자막 올린거
    @classmethod    
    def discord_cdn(cls, byteio=None, filepath=None, filename=None, webhook_url="https://discord.com/api/webhooks/1050549730964410470/ttge1ggOfIxrCSeTmYbIIsUWyMGAQj-nN6QBgwZTqLcHtUKcqjZ8wFWSWAhHmZne57t7", content='', retry=True):
        data = None
        if webhook_url is None:
            webhook_url =  webhook_list[random.randint(0,9)] 

        try:
            webhook = DiscordWebhook(url=webhook_url, content=content)
            if byteio is None and filepath is not None:
                import io
                with open(filepath, 'rb') as fh:
                    byteio = io.BytesIO(fh.read())
                
            webhook.add_file(file=byteio.getvalue(), filename=filename)
            embed = DiscordEmbed()
            response = webhook.execute()
            data = None
            if type(response) == type([]):
                if len(response) > 0:
                    data = response[0].json()
            else:
                data = response.json()    
            
            if data is not None and 'attachments' in data:
                target = data['attachments'][0]['url']
                if requests.get(target).status_code == 200:
                    return target
            if retry:
                time.sleep(1)
                return cls.discord_proxy_image_localfile(filepath, retry=False)
        except Exception as e: 
            logger.error(f"Exception:{str(e)}")
            logger.error(traceback.format_exc())
            if retry:
                time.sleep(1)
                return cls.discord_proxy_image_localfile(filepath, retry=False)
                
