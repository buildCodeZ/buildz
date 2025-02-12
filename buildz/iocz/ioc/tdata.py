#
from .tdict import TDict
from buildz import pyz, dz
class Key:
    Pub = "pub"
    Pri = "pri"
    Ns = "ns"
    tags_ns = "ns,pub".split(",")
    tags_pub = ['pub']
    tags_pri = None
pass
class TData(TDict):
    '''
        分成三个域，公共pub，私有pri和同域名ns
        不同域名只能访问pub数据
        同域名访问pub和ns
        同一个配置文件内（同一个id）访问pub，ns和pri
    '''
    def init(self, id=None, ns=None):
        self.ns = ns
        self.id = id
        super().init(Key.Pub)
    def call(self, *a,**b):
        return self.tget(*a,**b)
    def nsid(self, src, id):
        if isinstance(src, TData):
            ns = src.ns
            id = src.id
        else:
            ns = src
        return ns, id
    def tget(self, key, src=None, id=None):
        ns, id = self.nsid(src, id)
        if id == self.id:
            tags = Key.tags_pri
        elif ns == self.ns:
            tags = Key.tags_ns
        else:
            tags = Key.tags_pub
        return self.get(key, tags)

pass
