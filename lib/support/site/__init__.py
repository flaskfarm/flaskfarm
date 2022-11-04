import os

from support import SupportSC

try:
    if os.path.exists(os.path.join(os.path.dirname(__file__), 'tving.py')):
        #from .cppl import SupportCppl
        from .kakaotv import SupportKakaotv
        from .seezn import SupportSeezn
        from .tving import SupportTving
        from .wavve import SupportWavve
    else:
        SupportTving = SupportSC.load_module_f(__file__, 'tving').SupportTving
        SupportWavve = SupportSC.load_module_f(__file__, 'wavve').SupportWavve
        SupportSeezn = SupportSC.load_module_f(__file__, 'seezn').SupportSeezn
        SupportKakaotv = SupportSC.load_module_f(__file__, 'kakaotv').SupportKakaotv
        #SupportCppl = SupportSC.load_module_f(__file__, 'cppl').SupportCppl
except:
    pass
