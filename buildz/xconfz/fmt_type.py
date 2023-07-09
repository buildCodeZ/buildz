#coding=utf-8
from buildz.xconfz.base import *
from buildz.xconfz.fc_list import *
from buildz.xconfz.fc_set import *

from buildz.xconfz.fmt_base import *

"""
二元符<val, type>

"""

class TypeDealAFormat(BaseFormat):
    def __init__(self, left, right, spt):
        self.left = left
        self.right = right
        self.spt = spt
        self._types = {}
    def types(self, maps):
        self._types = dict(maps)
    def deal(self, node, fc, **params):
        if not node.is_leaf():
            return None
        val = node.value
        _type = type(val)
        if _type not in self._types:
            return None
        _fc = self._types[_type]
        sval, stype = _fc(val)
        spt = self.spt
        s = self.left+sval+spt+stype+self.right
        return s

pass

"""
二元符val|type
"""
class TypeDealBFormat(BaseFormat):
    def __init__(self, spt):
        self.spt = spt
        self._types = {}
    def types(self, maps):
        self._types = dict(maps)
    def deal(self, node, fc, **params):
        if not node.is_leaf():
            return None
        val = node.value
        _type = type(val)
        if _type not in self._types:
            return None
        _fc = self._types[_type]
        sval, stype = _fc(val)
        return sval+self.spt+stype

pass


class TypesDealFormat(BaseFormat):
    def __init__(self):
        self.deals = []
        self.types = {}
    def add_deal(self, deal):
        self.deals.append(deal)
        return self
    def add_type(self, key, fc):
        self.types[key] = fc
        return self
    def add(self, obj, fc = None):
        if isinstance(obj, BaseDeal):
            return self.add_deal(obj)
        else:
            return self.add_type(obj, fc)
    def init(self):
        for deal in self.deals:
            deal.types(self.types)
    def deal(self, node, fc, **params):
        for deal in self.deals:
            obj = deal.deal(node, fc, **params)
            if obj is not None:
                return obj
        return None

pass


