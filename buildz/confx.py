#
from .base import Base
'''
    新的buildz.confz
'''
class Confz(Base):
    def init(self, fc_key = "fc", fn_key = "fn", objs="__confz.objs", fns = "__confz.fns", caches = "__confz.caches", fcs = "__confz.fcs", default_fn = "calls", obj_prefix = "", save_key = "save", default_save = True):
        '''
            初始化的入参除了default_save，都是存储数据的字段的key
        '''
        self.fc_key = fc_key
        self.fn_key = fn_key
        self.objs = objs
        self.fns = fns
        self.fcs = fcs
        self.caches = caches
        self.default_fn = default_fn
        self.obj_prefix=  obj_prefix
        self.default_save = default_save
        self.save_key = save_key
    def set(self, conf, id, obj, prefix=True):
        '''
            存放创建好的对象
        '''
        if prefix:
            id = self.obj_prefix+id
        conf(self.objs).set(id, obj)
    def get(self, conf, id):
        id = self.obj_prefix+id
        objs = conf(self.objs)
        obj = objs.get(id)
        if obj is None:
            obj = self.simple(conf, id)
        return obj
    def regist(self, curr, conf):
        '''
            fn: regist/reg
            name: fn_name
            path: fc_path
            call: false
        '''
        name, path, call = curr.gets("name, path, call")
        if not call:
            fns = conf(self.fns)
            fns.set(name, path)
            return
        fc = pyz.load(path)
        fc = fc(curr, conf)
        conf(self.fcs).set(name, fc)
    def calls(self, curr, conf):
        """
            fn: calls
            calls: [key1, key2, key3]
        """
        calls = curr.get("calls", [])
        rst = [self.simple(conf, k) for k in calls]
        return rst
    def init(self, conf):
        fcs = conf(self.fcs)
        fcs.set("regist", self.regist)
        fcs.set("reg", self.regist)
        fcs.set("calls", self.calls)
    def get_fc(self, curr, conf, default_fc):
        s_fc = curr.get(self.fc_key, None)
        if s_fc is not None:
            return pyz.load(s_fc)
        if default_fc is not None:
            return default_fc
        fn = curr.get(self,fn_key, self.default_fn)
        fcs = conf(self.fcs)
        fc = fcs.get(fn)
        if fc is not None:
            return fc
        fns = conf(self.fns)
        s_fc = fns.get(fn)
        if s_fc is None:
            return None
        fc = pyz.load(s_fc)
        fcs.set(fn, fc)
        return fc
    def simple(self, conf, key, default_fc = None):
        curr = conf(key)
        fc = self.get_fc(curr, conf, default_fc)
        obj = fc(curr, conf)
        if curr.get(self.save_key, self.default_save):
            self.set(key, obj,False)
        return obj
    def call(self, conf, key, default_fc=None):
        return self.simple(conf, key, default_fc)

pass
                
def wrap(fc, to_dict=0, unwrap=0, put_conf=1):
    '''
        封装函数，封装成Confz调用的方法的形式fc(curr, conf)
        fc(**dict): wrap(fc, to_dict=1, unwrap=1)
        fc(dict): wrap(fc, to_dict=1, unwrap=0, put_conf=0)
        fc(dict, conf): wrap(fc, to_dict=1, unwrap=0, put_conf=0)
        fc(curr): wrap(fc, to_dict=0, unwrap=0, put_conf=0)
        fc(curr, conf): wrap(fc, to_dict=0, unwrap=0, put_conf=1)
    '''
    if unwrap:
        assert to_dict==1
        assert put_conf==0
    def wfc(curr, conf):
        if to_dict:
            curr = curr.dict()
        if unwrap:
            return fc(**curr)
        elif not put_conf:
            return fc(curr)
        else:
            return fc(curr, conf)
    return wfc

pass