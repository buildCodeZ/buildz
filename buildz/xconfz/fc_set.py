#coding=utf-8
from buildz.xconfz.base import *

class TypeSet:
    def __str__(self):
        return "@@TypeSet"
    def __repr__(self):
        return str(self)

pass
class SetDeal(BaseDeal):
    Type = TypeSet()
    def __str__(self):
        return "@@SetDeal"
    def __repr__(self):
        return str(self)
    def find(self, buff):
        for spt in self.spts:
            if self.check_curr(buff, spt):
                return spt
        return None
    def __init__(self, *spts):
        if len(spts)==0:
            raise Exception("at least one symbol")
        self.spts= spts
    def init(self, reg):
        self.k_spts = [reg(k) for k in self.spts]
        self.k_spt = self.k_spts[0]
    def prev(self, buff, queue):
        find = self.find(buff)
        if find is None:
            return False
        lf = len(find)
        rm = buff.remain().strip()
        pos = buff.pos_remain()
        c_pos = buff.pos_curr()
        if len(queue)==0 or len(rm)>0:
            queue.append(Item(rm, pos))
        queue.append(Item(self.k_spt, c_pos, find, SetDeal.Type))
        buff.deal2curr(lf)
        return True
    def deal(self, queue, stack):
        if len(stack)<3:
            return False
        if self.k_spt(stack[-2].val):
            if len(queue)>0:
                val = queue[0]
                if val.type == SetDeal.Type:
                    return False
            val = stack[-1]
            if Key.is_inst(val.val):
                return False
            val = stack.pop(-1)
            tmp = stack.pop(-1)
            key = stack.pop(-1)
            kv = KeyVal(key.val,val.val)
            item = Item(kv, key.pos)
            stack.append(item)
            return True
        return False