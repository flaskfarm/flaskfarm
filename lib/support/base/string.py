import re

from . import logger


class SupportString(object):
    @classmethod
    def get_cate_char_by_first(cls, title):  # get_first
        value = ord(title[0].upper())
        if value >= ord('0') and value <= ord('9'): return '0Z'
        elif value >= ord('A') and value <= ord('Z'): return '0Z'
        elif value >= ord('가') and value < ord('나'): return '가'
        elif value < ord('다'): return '나'
        elif value < ord('라'): return '다'
        elif value < ord('마'): return '라'
        elif value < ord('바'): return '마'
        elif value < ord('사'): return '바'
        elif value < ord('아'): return '사'
        elif value < ord('자'): return '아'
        elif value < ord('차'): return '자'
        elif value < ord('카'): return '차'
        elif value < ord('타'): return '카'
        elif value < ord('파'): return '타'
        elif value < ord('하'): return '파'
        elif value <= ord('힣'): return '하'
        else: return '0Z'
    

    @classmethod
    def is_include_hangul(cls, text):
        try:
            hanCount = len(re.findall(u'[\u3130-\u318F\uAC00-\uD7A3]+', text))
            return hanCount > 0
        except:
            return False

    @classmethod
    def language_info(cls, text):
        try:
            text = text.strip().replace(' ', '')
            all_count = len(text)
            han_count = len(re.findall('[\u3130-\u318F\uAC00-\uD7A3]', text))
            eng_count = len(re.findall('[a-zA-Z]', text))
            han_percent = int(han_count * 100 / all_count)
            eng_percent = int(eng_count * 100 / all_count)
            return (han_percent, eng_percent)
        except:
            return False
