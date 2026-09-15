
from .base import *
from .data import Data
class Datas(Base):
    def str(self):
        return f"<Datas>"+self.build_xml()+"</Datas>"
    def init(self, data_from_json, do_json=True, tag=None):
        '''
            data_from_json: 从dict生成实际对象
            do_json: 是否json，非json则是xml
            tag:只有xml有用，非xml不需要管
            使用xml则tag需要非空，并且要修改work方法里的not do_json逻辑里的代码
        '''
        self.do_json = do_json
        self.data_from_json = data_from_json
        self.tag = tag
        self.datas = []
    def _search(self, key, val):
        rst = [k for k in self.datas if getattr(k, key)==val]
        return rst
    def add(self, data):
        self.datas.append(data)
        return data
    def find(self, obj):
        for i in range(len(self.datas)):
            if self.datas[i].match(obj):
                return i
        return -1
    def replace(self, src, rpl):
        find = self.remove(src)
        if find is None:
            return None
        return self.add(rpl)
        find = self.find(src)
        if find<0:
            print(f"error do replace on {rp}: not found")
            return None
        self.datas[find] = rpl
        return rpl
    def remove(self, dt):
        find = self.find(dt)
        if find<0:
            print(f"error do del on {rm}: not found")
            return None
        return self.datas.pop(find)
    def build_json(self, abs=None):
        datas = [self.wrap_json(dt.out_json(abs)) for dt in self.datas]
        return datas
    def build_xml(self, abs=None):
        datas = [self.wrap_xml(self.tag, dt.out_xml(abs)) for dt in self.datas]
        datas = "".join(datas)
        return datas
    def wrap_json(self, obj):
        return obj
    def wrap_xml(self, tag, s):
        return xml.w(tag, s)
    def work(self, obj):
        '''
            获取增删改数据，做增删改
        '''
        out_rps, out_incs, out_dels = [],[],[]
        if self.do_json:
            incs, dels, rps = dz.g(obj, increments=[], removes=[], replaces = [])
        else:
            # 老代码，需要改造后使用
            incs = xml.arr(obj, "increments", "increment")
        def clean(arr):
            return [k for k in arr if k is not None]
        for rp in rps:
            out_rps += clean([self.do_replace(rp)])
        for inc in incs:
            out_incs += clean([self.do_inc(inc)])
        for rm in dels:
            out_dels += clean([self.do_remove(rm)])
        return out_rps, out_incs, out_dels
    def do_remove(self, rm):
        rm = xml.x2j(rm)
        dt = self.data_from_json(rm)
        return self.remove(dt)
    def do_inc(self, inc):
        inc = xml.x2j(inc)
        dt = self.data_from_json(inc)
        return self.add(dt)
    def do_replace(self, rp):
        rp = xml.x2j(rp)
        src = rp.get("source", {})
        rpl = rp.get("target", {})
        src = self.data_from_json(src)
        rpl = self.data_from_json(rpl)
        return self.replace(src, rpl)
