
import os
import traceback

from framework import F


class Util(object):

    @staticmethod
    def db_to_dict(db_list):
        ret = []
        for item in db_list:
            ret.append(item.as_dict())
        return ret

    @staticmethod
    def get_paging_info(count, current_page, page_size):
        try:
            paging = {}
            paging['prev_page'] = True
            paging['next_page'] = True
            if current_page <= 10:
                paging['prev_page'] = False
            
            paging['total_page'] = int(count / page_size) + 1
            if count % page_size == 0:
                paging['total_page'] -= 1
            paging['start_page'] = int((current_page-1)/10) * 10 + 1
            paging['last_page'] = paging['total_page'] if paging['start_page'] + 9 > paging['total_page'] else paging['start_page'] + 9
            if paging['last_page'] == paging['total_page']:
                paging['next_page'] = False
            paging['current_page'] = current_page
            paging['count'] = count
            F.logger.debug('paging : c:%s %s %s %s %s %s', count, paging['total_page'], paging['prev_page'], paging['next_page'] , paging['start_page'], paging['last_page'])
            return paging
        except Exception as e:
            F.logger.debug(f"Exception:{str(e)}")
            F.logger.debug(traceback.format_exc())
    

    # 토렌트 인포에서 최대 크기 파일과 폴더명을 리턴한다
    @staticmethod
    def get_max_size_fileinfo(torrent_info):
        try:
            ret = {}
            max_size = -1
            max_filename = None
            for t in torrent_info['files']:
                if t['size'] > max_size:
                    max_size = t['size']
                    max_filename = str(t['path'])
            t = max_filename.split('/')
            ret['filename'] = t[-1]
            if len(t) == 1:
                ret['dirname'] = ''
            elif len(t) == 2:
                ret['dirname'] = t[0]
            else:
                ret['dirname'] = max_filename.replace('/%s' % ret['filename'], '')
            ret['max_size'] = max_size
            return ret
        except Exception as e: 
            F.logger.error(f"Exception:{str(e)}")
            F.logger.error(traceback.format_exc())


    # 압축할 폴더 경로를 인자로 받음. 폴더명.zip 생성
    @staticmethod
    def makezip(zip_path, zip_extension='zip'):
        import zipfile
        try:
            if os.path.isdir(zip_path):
                zipfilename = os.path.join(os.path.dirname(zip_path), '%s.%s' % (os.path.basename(zip_path), zip_extension))
                fantasy_zip = zipfile.ZipFile(zipfilename, 'w')
                for f in os.listdir(zip_path):
                    #if f.endswith('.jpg') or f.endswith('.png'):
                        src = os.path.join(zip_path, f)
                        fantasy_zip.write(src, os.path.basename(src), compress_type = zipfile.ZIP_DEFLATED)
                fantasy_zip.close()
            import shutil
            shutil.rmtree(zip_path)
            return True
        except Exception as e:
            F.logger.error(f"Exception:{str(e)}")
            F.logger.error(traceback.format_exc())
        return False



    @staticmethod
    def make_apikey(url):
        from framework import SystemModelSetting
        url = url.format(ddns=SystemModelSetting.get('ddns'))
        if SystemModelSetting.get_bool('use_apikey'):
            if url.find('?') == -1:
                url += '?'
            else:
                url += '&'
            url += 'apikey=%s' % SystemModelSetting.get('apikey')
        return url



