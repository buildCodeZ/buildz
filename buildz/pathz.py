from . import Base
import os,sys,json,time
class Path(Base):
    def init(self, **maps):
        self.paths = {}
        self.fcs = {}
        self.lasts = {}
        for k, v in maps.items():
            self.set(k, v)
    @staticmethod
    def join(*a):
        return os.path.join(*a)
    @staticmethod
    def rjoin(path, *a):
        if path is None:
            return os.path.join(*a)
        return os.path.join(path, *a)
    @staticmethod
    def rfp(paths, *a, last=-1):
        #print(f"[TESTZ] a: {a}, paths: {paths}")
        #fp = os.path.join(*a)
        for path in paths:
            _fp = Path.rjoin(path, *a)
            if os.path.exists(_fp):
                return _fp
        return Path.rjoin(paths[last], *a)
    def add(self, name, path, index=0):
        self.paths[name].insert(index, path)
    def set(self, name, paths, last = -1, curr = None):
        if type(paths) not in (list, tuple):
            paths = [paths]
        if curr is not None and None not in paths:
            if curr in (0, 'first'):
                paths = [None]+paths
            elif curr in (-1, 'last'):
                paths.append(None)
            else:
                assert False
        self.paths[name] = paths
        self.lasts[name] = last
        def fc(*a):
            return self.rfp(paths, *a, last=last)
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
