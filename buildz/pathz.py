from . import Base
import os,sys,json,time
class Path(Base):
    def init(self, **maps):
        self.paths = {}
        self.fcs = {}
        for k, v in maps.items():
            self.set(k, v)
    @staticmethod
    def join(*a):
        return os.path.join(*a)
    def set(self, name, path):
        self.paths[name] = path
        def fc(*a):
            return self.join(path, *a)
        self.fcs[name] = fc
    def __getattr__(self, name):
        return self.fcs[name]
    def call(self, *obj):
        it = obj[0]
        fc = self.join
        if type(it) in (list, tuple):
            assert len(it)==2
            k, fp = it
            fc = self.fcs[k]
        rst = []
        for it in obj:
            if type(it) in (list, tuple):
                assert len(it)==2
                rst.append(it[1])
        return fc(*rst)

pass
