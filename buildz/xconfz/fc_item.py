#coding=utf-8
from buildz.xconfz.base import *


"""
去左空格
"""
class SpcDeal(BaseDeal):
    def prev(self, buff, stack):
        if buff.remain_size()==0:
            c = buff.curr()
            if len(c.strip())==0 and len(c)>0:
                buff.deal2curr()
                return True
        return False

pass

"""
没有其他处理的默认处理：当前字符放入保留字符串，读取下一个字符
"""
class NextCharDeal(BaseDeal):
    def prev(self, buff, queue):
        #print("SRC:", buff.remain()," : ", buff.curr(100))
        rst= buff.add_remain()
        #print("ADD:", buff.remain(), " : " ,buff.curr(100))
        return rst
    def deal(self, queue, stack):
        if len(queue)==0:
            return False
        stack.append(queue.pop(0))
        return True

pass

"""
分割符判断
"""
class ItemDeal(BaseDeal):
    def find(self, buff):
        for spt in self.spts:
            if self.check_curr(buff, spt):
                return spt
        return None
    def __init__(self, *args):
        if len(args)==0:
            raise Exception("at least one symbol")
        self.spts= args
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
        if len(queue)==0 or len(rm)>0 or self.k_spt(queue[-1].val):
            #print("val:[{rm}]".format(rm=rm))
            queue.append(Item(rm, pos))
        queue.append(Item(self.k_spt, c_pos, find))
        buff.deal2curr(lf)
        return True
    def deal(self, queue, stack):
        if len(queue)==0:
            return False
        it = queue[0]
        if self.k_spt(it.val):
            queue.pop(0)
            return True
        return False

pass
