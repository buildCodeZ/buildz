#coding=utf-8
from buildz.xconfz.base import *


class StrDeal(BaseDeal):
    def __init__(self, left = '"', right= '"', single_line = False, note = False):
        self.left = left
        self.right = right
        self.single_line = single_line
        self.note = note
    def init(self,reg):
        self.k_l = reg(self.left)
        if self.left == self.right:
            self.k_r = self.k_l
        else:
            self.k_r = reg(self.right)
    def prev(self, buff, queue):
        if not self.check_curr(buff, self.left):
            return False
        rm = buff.remain().strip()
        if len(rm)>0 and not self.note:
            raise FormatExp("str: unexcept char before symbol:", buff.pos_remain(), rm)
        left_pos = buff.pos_curr()
        buff.deal2curr(len(self.left))
        lr = len(self.right)
        curr = buff.curr(lr)
        while len(curr)>=lr:
            if curr == self.right:
                s = buff.remain()
                if not self.note:
                    queue.append(Item(s, left_pos))
                elif len(rm)>0:
                    queue.append(Item(rm, left_pos))
                buff.deal2curr(lr)
                return True
            if self.single_line and curr.find("\n")>=0:
                raise FormatExp("str|note: unexcept enter for string", buff.pos_remain())
            buff.add_remain(1)
            curr = buff.curr(lr)
        print(buff.remain())
        err = "str|note: can't find right symbol {right} for left symbol {left}".format(right =  self.right, left = self.left)
        raise FormatExp(err, left_pos)

pass

class TranslateStrDeal(StrDeal):
    def prev(self, buff, queue):
        if not self.check_curr(buff, self.left):
            return False
        rm = buff.remain().strip()
        if len(rm)>0:
            raise FormatExp("str|note: unexcept char before symbol:", buff.pos_remain())
        left_pos = buff.pos_curr()
        buff.deal2curr(len(self.left))
        lr = len(self.right)
        cnt = 0
        curr = buff.curr(1)
        mark = False
        while len(curr)>0:
            cnt += 1
            if curr in ["\\", b"\\"] and not mark:
                mark = True
            else:
                rm += curr
                if mark:
                    cnt = 0
                mark = False
            if not mark and cnt >= lr:
                if rm[-lr:] == self.right:
                    rm = rm[:-lr]
                    if not self.note:
                        queue.append(Item(rm, left_pos))
                    buff.deal2curr(1)
                    return True
            buff.add_remain(1)
            curr = buff.curr(1)
        err = "str|note: can't find right symbol {right} for left symbol {left}".format(right =  self.right, left = self.left)
        raise FormatExp(err, left_pos)

pass