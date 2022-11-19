import base64
import os
import traceback

from Crypto import Random
from Crypto.Cipher import AES

from . import logger

BS = 16
pad = lambda s: s + (BS - len(s.encode('utf-8')) % BS) * chr(BS - len(s.encode('utf-8')) % BS) 
#unpad = lambda s : s[0:-s[-1]]
unpad = lambda s : s[:-ord(s[len(s)-1:])]
key = b'140b41b22a29beb4061bda66b6747e14'

class SupportAES(object):
    @classmethod
    def encrypt(cls, raw, mykey=None):
        try:
            Random.atfork()
        except Exception as e: 
            logger.error(f"Exception:{str(e)}")
            logger.error(traceback.format_exc()) 

        raw = pad(raw)
        if type(raw) == type(''):
            raw = raw.encode()
        if mykey is not None and type(mykey) == type(''):
            mykey = mykey.encode()
        iv = Random.new().read( AES.block_size )
        cipher = AES.new(key if mykey is None else mykey, AES.MODE_CBC, iv )
        try:
            tmp = cipher.encrypt( raw )
        except Exception as e: 
            logger.error(f"Exception:{str(e)}")
            logger.error(traceback.format_exc()) 
            tmp = cipher.encrypt( raw.encode() )
        ret = base64.b64encode( iv + tmp ) 
        ret = ret.decode()
        return ret

    @classmethod
    def decrypt(cls, enc, mykey=None):
        enc = base64.b64decode(enc)
        iv = enc[:16]
        if len(iv) != 16:
            iv = os.urandom(16)
        if mykey is not None and type(mykey) == type(''):
            mykey = mykey.encode()
        cipher = AES.new(key if mykey is None else mykey, AES.MODE_CBC, iv )
        return unpad(cipher.decrypt( enc[16:] )).decode()

    @classmethod
    def md5(cls, text):
        import hashlib
        enc = hashlib.md5()
        enc.update(text.encode())
        return enc.hexdigest()
    



    @classmethod
    def encrypt_(cls, raw, mykey=None, iv=None):
        try:
            Random.atfork()
        except Exception as e: 
            logger.error(f"Exception:{str(e)}")
            logger.error(traceback.format_exc()) 
        raw = pad(raw)
        if type(raw) == type(''):
            raw = raw.encode()
        if mykey is not None and type(mykey) == type(''):
            mykey = mykey.encode()
        if iv == None:
            iv = Random.new().read( AES.block_size )
        elif iv is not None and type(iv) == type(''):
            iv = iv.encode()
        cipher = AES.new(key if mykey is None else mykey, AES.MODE_CBC, iv )
        try:
            tmp = cipher.encrypt( raw )
        except Exception as e: 
            logger.error(f"Exception:{str(e)}")
            logger.error(traceback.format_exc()) 
            tmp = cipher.encrypt( raw.encode() )
        ret = base64.b64encode( tmp ) 
        ret = ret.decode()
        return ret

    @classmethod
    def decrypt_(cls, enc, mykey=None, iv=None):
        enc = base64.b64decode(enc)
        if iv == None:
            iv = os.urandom(16)
        elif iv is not None and type(iv) == type(''):
            iv = iv.encode()
        if mykey is not None and type(mykey) == type(''):
            mykey = mykey.encode()
        cipher = AES.new(key if mykey is None else mykey, AES.MODE_CBC, iv )
        return unpad(cipher.decrypt( enc )).decode()
