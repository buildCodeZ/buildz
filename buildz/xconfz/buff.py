#coding=utf-8

from buildz.xconfz.base import *

class BufferImpl(Buffer):
    def cal_pos(self, s):
        n = "\n"
        if type(s)==bytes:
            n = b"\n"
        arr= s.split(n)
        return len(arr)-1, len(arr[-1])
    def __init__(self, reader, empty = ""):
        self._read = reader
        self._remain = empty
        self._curr = empty
        self.index = [0,0]
        self.row = [0,0]
        self._empty= empty
    def pos_remain(self):
        return self.row[0]+1, self.index[0]+1
    def pos_curr(self):
        return self.row[1]+1, self.index[1]+1
    def curr(self, size = 1):
        if self._curr is None:
            self._curr = self._read(size)
        elif len(self._curr)<size:
            ch = self._read(size-len(self._curr))
            if len(ch)==0:
                return self._curr
            self._curr += ch
        return self._curr[:size]
    def remain_size(self):
        return 0 if self._remain is None else len(self._remain)
    def remain(self):
        return self._remain
    def deal_remain(self):
        self.index[0] = self.index[1]
        self.row[0] = self.row[1]
        self._remain= self._empty
    def add_remain(self,size=1):
        curr = self.curr(size)
        if len(curr)<size:
            return False
        row, id = self.cal_pos(curr)
        if row == 0:
            self.index[1]+=id
        else:
            self.row[1]+=row
            self.index[1]= id
        self._remain+=curr
        self._curr = self._curr[size:]
        return True
    def deal2curr(self, size = 1):
        bl = self.add_remain(size)
        self.deal_remain()

pass
