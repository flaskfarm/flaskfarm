import copy
import os
import re
import time
import traceback
import uuid
from base64 import b64encode
from datetime import datetime

import requests
from support import SupportFile, d, default_headers, logger

try:
    from lxml import html
except:
    os.system("pip install lxml")
    from lxml import html

try:
    import wv_tool
except:
    pass

class SupportKakaotv:
    uu = str(uuid.uuid4()).replace('-', '')

    @classmethod
    def get_recent_channel(cls):
        res = requests.get('https://tv.kakao.com/top')
        root = html.fromstring(res.text)
        #logger.debug(root)

        tags = root.xpath('//div[@class="area_category"]')
        #logger.debug(tags)
        now = datetime.now()
        item_list = []
        for tag in tags:
            entity = {'episodes':[]}
            entity['title'] = tag.xpath('.//span[@class="txt_subject"]')[0].text
            first_item = tag.xpath('.//div[@class="inner_favoritem"]')[0]
            link = first_item.xpath('.//a')[0].attrib['href']
            entity['channel_id'] = link.split('/')[2]
            entity['upload_time'] = first_item.xpath('.//a/span[3]/span[2]/span[2]')[0].attrib['data-raw-date']
            upload_time = datetime.strptime(entity['upload_time'], '%Y-%m-%d %H:%M:%S')
            if (now - upload_time).days > 10:
                break
            item_list.append(entity)
        return item_list


    @classmethod 
    def get_video_list(cls, channel_id):
        try:
            ret = []
            root = html.fromstring(requests.get(f"https://tv.kakao.com/channel/{channel_id}/playlist", headers=default_headers).text)
            tags = root.xpath('//*[@id="mArticle"]/div[2]/ul/li[1]')
            for tag in tags:
                name = tag.xpath('a/span[2]/strong')[0].text
                
                if name.find('본편') != -1:
                    channel_name = re.match(r'\[(.*?)\]', name).group(1).strip()
                    playlist_url = f"https://tv.kakao.com{tag.xpath('a')[0].attrib['href']}"
                    playlist_root = html.fromstring(requests.get(playlist_url).text)
                    playlist_item_tags = playlist_root.xpath('//*[@id="playerPlaylist"]/ul[1]/li')
                    for playlist_item in playlist_item_tags:
                        episode_entity = {'channel_id':channel_id, 'channel_name':channel_name}
                        episode_entity['link'] = 'https://tv.kakao.com' + playlist_item.xpath('a')[0].attrib['href']
                        episode_entity['clip_id'] = playlist_item.xpath('a')[0].attrib['href'].split('?')[0].split('/')[-1]
                        episode_entity['no'] = int(playlist_item.xpath('a/span[1]')[0].text)
                        episode_entity['title'] = playlist_item.xpath('a/span[3]/strong')[0].text
                        episode_entity['img'] = 'https:' + playlist_item.xpath('a/span[2]/img')[0].attrib['src']
                        match = re.match(r"(\d+)회", episode_entity['title'])
                        if match:
                            episode_entity['no'] = int(match.group(1))
                        try:
                            episode_entity['pay'] = playlist_item.xpath('a/span[3]/span/span')[0].text
                            #continue
                        except:
                            episode_entity['pay'] = '무료'
                        episode_entity['filename'] = '{title}.S{season_number}E{episode_number}.1080p.WEB-DL.AAC.H.264.SW{site}.mkv'.format(
                            title = SupportFile.text_for_filename(channel_name),
                            season_number = str(1).zfill(2),
                            episode_number = str(episode_entity['no']).zfill(2),
                            site = 'KK',
                        )
                        ret.append(episode_entity)
                    ret = list(reversed(ret))
            return ret
        except Exception as e:
            logger.error(f'Exception:{str(e)}')
            logger.error(traceback.format_exc())

    @classmethod
    def make_wvtool_config(cls, info):
        timestamp = str(time.time()*1000).split('.')[0]
        url = f"https://tv.kakao.com/katz/v4/ft/cliplink/{info['clip_id']}/readyNplay?player=monet_html5&referer=&uuid={cls.uu}&profile=HIGH4&service=kakao_tv&section=channel&fields=seekUrl,abrVideoLocationList&playerVersion=3.14.1&appVersion=106.0.0.0&startPosition=0&tid=&dteType=PC&continuousPlay=false&autoPlay=false&contentType=&drmType=widevine&ab=&literalList=&{timestamp}"

        data = requests.get(url, headers=default_headers).json()
        vid = data['vmapReq']['content_data']['vid']
        tid = data['tid']

        headers = copy.deepcopy(default_headers)
        headers['x-kamp-auth'] = f"Bearer {data['kampLocation']['token']}"
        url = f"https://kamp.kakao.com/vod/v1/src/{vid}?tid={tid}&param_auth=true&{timestamp}"
        data = requests.get(url, headers=headers).json()
        
        mpd_headers = copy.deepcopy(default_headers)
        mpd_headers['Origin'] = 'https://tv.kakao.com'
        mpd_headers['Referer'] = 'https://tv.kakao.com/'
        mpd_url = data['streams'][0]['url']

        if data['is_drm']:
            return {
                'logger' : logger,
                'mpd_url' : mpd_url,
                'code' : info['clip_id'],
                'output_filename' : info['filename'],
                'mpd_headers': mpd_headers,
                'clean' : False,
                'license_url': 'https://drm-license.kakaopage.com/v1/license',
                'attach_url_param': '?' + mpd_url.split('?')[1],
                'vars' : {
                    'data': data
                }
            }
        else:
            return None



    try:
        import wv_tool 
        class WVDownloaderKakao(wv_tool.WVDownloader):
            def do_make_key(self):
                postdata = {}
                postdata = copy.deepcopy(default_headers)
                postdata['headers'] = {}
                postdata['headers']['Host'] = 'drm-license.kakaopage.com'
                postdata['headers']['Origin'] = 'https://tv.kakao.com'
                postdata['headers']['Referer'] = 'https://tv.kakao.com/'
                postdata['data'] = {}
                postdata['data']['token'] = self.config['vars']['data']['drm']['token']
                postdata['data']['provider'] = self.config['vars']['data']['drm']['provider']
                
                wv = wv_tool.WVDecryptManager(self.pssh)
                payload = wv.get_challenge()
                payload = b64encode(payload)
                payload = payload.decode('ascii')
                postdata['data']['payload'] = payload
                widevine_license = requests.post(url=self.license_url, data=postdata['data'], headers=postdata['headers'])
                data = widevine_license.json()
                #logger.error(d(data))
                license_b64 = data['payload']
                correct, keys = wv.get_result(license_b64)
                
                if correct:
                    for key in keys:
                        tmp = key.split(':')
                        self.key.append({'kid':tmp[0], 'key':tmp[1]})
            
    except Exception as e: 
        logger.error('Exception:%s', e)
        logger.error(traceback.format_exc())


"""
url = "https://tv.kakao.com/embed/player/cliplink/433009293?service=kakao_tv&section=channel&autoplay=1&profile=HIGH4&wmode=transparent"


url = "https://play-tv.kakao.com/katz/v1/close/cliplink/433009293/info"

"""
