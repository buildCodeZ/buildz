
from .base import *
from ... import dz,pyz
from ..ioc.single import Single
class RefEncape(BaseEncape):
    '''
    '''
    def init(self, ref, default, unit):
        super().init()
        self.unit = unit
        self.ref, self.default = ref, default
    def call(self, params=None, **maps):
        ref = self.ref
        if isinstance(ref, Encape):
            ref = ref(params)
        obj, find = self.unit.get(ref)
        if not find:
            assert self.default[0], f"ref '{ref}' not found"
            val = self.default[1]
            if isinstance(val, Encape):
                val = val(params)
            obj = val
        return obj
class RefDeal(BaseDeal):
    def deal(self, conf, unit):
        assert 'ref' in conf, f"[REF] key 'ref' not found in {conf}"
        ref = dz.g(conf, ref=None)
        if 'default' in conf:
            default = 1,conf['default']
        else:
            default = 0,None
        ref = self.get_encape(ref, unit)
        if default[0]:
            default[1] = self.get_encape(default[1], unit)
        encape = RefEncape(ref, default, unit)
        return encape

pass