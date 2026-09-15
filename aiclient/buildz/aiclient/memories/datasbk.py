
import json, time, os
from buildz.base import Base
from buildz.html import base as xml
from buildz import xf,dz,fz, log as logz, path as pathz
from .data import Data
class Datas(Base):
    format="%Y-%m-%d %H:%M:%S"
    def str(self):
        return f"<Datas>"+self.build_xml()+"</Datas>"
    def sec2date(self, sec=None):
        sec = sec or time.time()
        return time.strftime(self.format, time.localtime(sec))
    def date2sec(self, date):
        assert False, 'not impl'
    def init(self, tag, do_json, data_from_json):
        self.do_json = do_json
        self.data_from_json = data_from_json
        self.tag = tag
        self.datas = []
    def build_json(self, abs=None):
        datas = [self.wrap_json(dt.out_json(abs)) for dt in self.datas]
        return datas
    def build_xml(self, abs=None):
        datas = [self.wrap_xml(self.tag, dt.out_xml(abs)) for dt in self.datas]
        datas = "".join(datas)
        return datas
    def wrap_json(self, obj, sec=None):
        if sec:
            date = self.sec2date(sec)
            obj['date'] = date
        return obj
    def wrap_xml(self, tag, s, sec=None):
        if sec:
            date = self.sec2date(sec)
            s = s+xml.xr(date=date)
        return xml.w(tag, s)
    def work(self, obj):
        '''
            获取增删改数据，做增删改
        '''
        out_rps, out_incs, out_dels = [],[],[]
        if self.do_json:
            incs, dels, rps = dz.g(obj, increments=[], removes=[], replaces = [])
        else:
            incs = xml.arr(obj, "increments", "increment")
            dels = xml.arr(obj, "removes", "remove")
            rps = xml.arr(obj, "replaces", "replace")
        def clean(arr):
            return [k for k in arr if k is not None]
        for rp in rps:
            out_rps+=clean([self.do_replace(rp)])
        for inc in incs:
            out_incs+=clean([self.do_inc(inc)])
        for rm in dels:
            out_dels += clean([self.do_del(rm)])
        return out_rps, out_incs, out_dels
    def find(self, obj):
        for i in range(len(self.datas)):
            if self.datas[i].match(obj):
                return i
        return -1
    def do_del(self, rm):
        rm = xml.x2j(rm)
        dt = self.data_from_json(rm)
        find = self.find(dt)
        if find<0:
            print(f"error do del on {rm}: not found")
            return None
        assert find>=0
        return self.datas.pop(find)
    def do_inc(self, inc):
        inc = xml.x2j(inc)
        dt = self.data_from_json(inc)
        dt.date = self.sec2date()
        self.datas.append(dt)
        return dt
    def do_replace(self, rp):
        rp = xml.x2j(rp)
        src = rp.get("source", {})
        rpl = rp.get("target", {})
        src = self.data_from_json(src)
        rpl = self.data_from_json(rpl)
        rpl.date = self.sec2date()
        find = self.find(src)
        if find<0:
            print(f"error do replace on {rp}: not found")
            return None
        assert find>=0
        self.datas[find] = rpl
        return rpl
