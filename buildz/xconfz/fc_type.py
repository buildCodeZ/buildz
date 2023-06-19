#coding=utf-8
from buildz.xconfz.base import *
from buildz.xconfz.fc_list import *
from buildz.xconfz.fc_set import *


"""
二元符<val, type>

"""

class TypeDealA(ListDeal):
    def __init__(self, left, right):
        super(TypeDealA, self).__init__(left, right)
        self._types = {}
    def types(self, maps):
        self._types = dict(maps)
    def deal(self, queue, stack):
        rst = super(TypeDealA, self).deal(queue, stack)
        if not rst:
            return False
        item = stack[-1]
        vals = item.val
        if Key.is_inst(vals):
            return True
        stack.pop(-1)
        if len(vals)!=2:
            raise FormatExp("type error: requires two elements", item.pos)
        val, _type = vals
        if _type not in self._types:
            raise FormatExp("type error: can't deal with type {type}".format(type = _type), item.pos)
        try:
            val = self._types[_type](val)
        except Exception as exp:
            raise FormatExp("type error: "+str(exp), item.pos)
        stack.append(Item(val, item.pos))
        return True

pass

"""
二元符val|type
"""
class TypeDealB(SetDeal):
    def __init__(self, *args):
        super(TypeDealB, self).__init__(*args)
        self._types = {}
    def types(self, maps):
        self._types = dict(maps)
    def deal(self, queue, stack):
        rst = super(TypeDealB, self).deal(queue, stack)
        if not rst:
            return False
        item = stack.pop(-1)
        vals = item.val
        val = vals.key
        _type = vals.val
        if _type not in self._types:
            raise FormatExp("type error: can't deal with type {type}".format(type = _type), item.pos)
        try:
            val = self._types[_type](val)
        except Exception as exp:
            raise FormatExp("type error: "+str(exp), item.pos)
        stack.append(Item(val, item.pos))
        return True

pass


class TypesDeal:
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
    def init(self, reg):
        for deal in self.deals:
            deal.types(self.types)
            deal.init(reg)
    def prev(self, buff, queue):
        for deal in self.deals:
            if deal.prev(buff, queue):
                return True
        return False
    def deal(self, queue, stack):
        for deal in self.deals:
            if deal.deal(queue, stack):
                return True
        return False

pass
