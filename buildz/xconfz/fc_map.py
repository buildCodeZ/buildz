#coding=utf-8
from buildz.xconfz.base import *

from buildz.xconfz.fmt_base import *

class MapDeal(BaseDeal):
    def init(self, reg):
        self.k_l = reg(self.l)
        self.k_r = reg(self.r)
    def __init__(self, left, right):
        self.l = left
        self.r = right
    def prev(self, buff, queue):
        if self.check_curr(buff,self.l):
            if buff.remain_size()>0:
                raise FormatExp("error string before map:", buff.pos_curr(), buff.full())
            queue.append(Item(self.k_l, buff.pos_curr()))
            buff.deal2curr(len(self.l))
            return True
        elif self.check_curr(buff, self.r):
            if buff.remain_size()>0:
                r = buff.remain().strip()
                if len(r)>0:
                    queue.append(Item(r, buff.pos_remain()))
            queue.append(Item(self.k_r, buff.pos_curr()))
            buff.deal2curr(len(self.r))
            return True
        return False
    def deal(self, queue, stack):
        if len(queue)==0:
            return False
        it = queue[0]
        rst = False
        if self.k_r.equal(it.val):
            tmp = []
            find_l = False
            while len(stack)>0:
                it_1 =  stack.pop(-1)
                if self.k_l.equal(it_1.val):
                    find_l = True
                    break
                val = it_1.val
                if not KeyVal.is_inst(val):
                    #print("it_1:", it_1)
                    #print("queue:", queue)
                    #print("stack:", stack)
                    #print("map:", tmp)
                    raise FormatExp("an not key-val item found in map:"+str(val), it_1.pos)
                tmp.append(val)
            tmp.reverse()
            tmp = {k.key:k.val for k in tmp}
            #tmp[val.key] = val.val
            if not find_l:
                raise FormatExp("can't find map left side for right side",it.pos)
            stack.append(Item(tmp, it_1.pos))
            rst = True
        elif self.k_l.equal(it.val):
            stack.append(it)
            rst = True
        if rst:
            queue.pop(0)
        return rst

pass

class MapFormat(BaseFormat):
    def __init__(self, left, right):
        self.l = left
        self.r = right 
    def deal(self, data, fc):
        if type(data) !=dict:
            raise FormatExp("not dict found:"+type(data), [-1,-1])
        node = FormatNode().init()
        node.add(SymbolFormatNode().init().val(self.l))
        #_node = FormatNode().init()
        #node.add(_node)
        nds = []
        for key in data:
            nds.append(SpcFormatNode(0,1))
            nds.append(fc(key))
            nds.append(KVFormatNode())
            nds.append(fc(data[key]))
            nds.append(SptFormatNode())
        for nd in nds[:-1]:
            node.add(nd)
        node.add(SpcFormatNode(0, 0))
        node.add(SymbolFormatNode().init().val(self.r))
        return node


pass