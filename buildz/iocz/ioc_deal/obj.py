
from ..ioc.base import *
from buildz import dz
class ObjectType(Base):
    Single=0
    Multi=1
    SingleVars=2

class ObjectCreater(Creater):
    def init(self, obj_type = ObjectType.Single):
        super().init()
        self.obj_type = obj_type
        self.args = []
        self.maps = {}
        self.sets = {}
        self.before_set = None
        self.after_set = None
        self.before_remove = None
        self.fc = None
        self.single = Single()
    def fills(self, params):
        _a, _m, _s = dz.g(params, args=[], maps={}, sets={})
        args = self.args
        args = _a+args[len(_a):]
        maps = dict(self.maps)
        maps.update(_m)
        sets = dict(self.sets)
        sets.update(_s)
        return args, maps, sets
    def single_id(self, params):
    def hash(self, params):
        if self.obj_type == ObjectType.Single or self.obj_type == ObjectType.Multi:
            return ""
        _a, _m, _s = dz.g(params, args=[], maps={}, sets={})
        args = self.args
        args = _a+args[len(_a):]
        maps = dict(self.maps)
        maps.update(_m)
        sets = dict(self.sets)
        sets.update(_s)
        args = [str(self.mg.hash(it)) for it in args]
        maps = [str(k)+":"+self.mg.hash(val) for k,val in maps.items()]
        sets = [str(k)+":"+self.mg.hash(val) for k,val in sets.items()]
        args = ",".join(args)
        maps = ",".join(maps)
        sets = ",".join(sets)
        val = [args, maps, self.mg.hash(self.before_set), sets, self.mg.hash(self.after_set)]
        return "|".join(val)
    def call(self, params):
        call_type = dz.g(params, type="create")
        if call_type == "remove":
            self.mg.deal()
        id = None
        if self.obj_type == ObjectType.Single:
            if self.single.has(id):
                return self.single.get(id)
        _a, _m, _s = dz.g(params, args=[], maps={}, sets={})
        args = self.args
        args = _a+args[len(_a):]
        maps = dict(self.maps)
        maps.update(_m)
        sets = dict(self.sets)
        sets.update(_s)
        if self.obj_type == ObjectType.SingleVars:
            id = self.hash(params)
            if self.single.has(id):
                return self.single.get(id)
        args = [self.mg.deal(it) for it in args]
        maps = {k:self.mg.deal(v) for k,v in maps.items()}
        obj = self.fc(*args, **maps)
        params = {'target':obj}
        self.mg.deal(self.before_set, params=params)
        sets = {k:self.mg.deal(v) for k,v in sets.items()}
        for k,v in sets:
            setattr(obj, k, v)
        self.mg.deal(self.after_set, params=params)
        if self.obj_type!=ObjectType.Multi:
            self.single.set(id, obj)
        return obj