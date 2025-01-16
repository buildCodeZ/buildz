#
from buildz import Base, xf
class Build(Base):
    def init(self, *binds):
        self.builder = None
        self.binds = binds
    def bind(self, builder):
        self.builder = builder
        for obj in self.binds:
            obj.bind(builder)
    def call(self, conf):
        assert 0, 'not impl'
class Builder(Base):
    def init(self, fc = None, key_id = "id"):
        self.vars = {}
        self.confs = {}
        self.key_id = key_id
        self.set_fc(fc)
    def set_fc(self, fc):
        fc.bind(self)
        self.fc = fc
        return self
    def var(self, key, obj):
        self.vars[key] = obj
        return self
    def get_var(self, key):
        return self.vars[key]
    def get_conf(self, key):
        if type(key) == dict:
            conf = key
        else:
            if key not in self.confs:
                return self.get_var(key)
            conf = self.confs[key]
        return self.fc(conf)
    def conf(self, data):
        if type(data) in (list, tuple):
            rst = {}
            for it in data:
                if self.key_id not in it:
                    continue
                id = it[self.key_id]
                rst[id] = it
            data = rst
        self.confs = data
        return self
    def call(self, data, key="main"):
        return self.conf(data).get_conf(key)
