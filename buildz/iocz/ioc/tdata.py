#
from .tdict import TagDict
from ... import pyz, dz
class Key:
    Pub = "pub"
    Pri = "pri"
    Ns = "ns"
    tags_ns = [Ns,Pub]
    tags_pub = [Pub]
    tags_pri = None
pass
class TagData(TagDict):
    '''
        分成三个域，公共pub，私有pri和同域名ns
        设置访问规则
        不同域名只能访问pub数据
        同域名访问pub和ns
        同一个配置文件内（同一个id）访问pub，ns和pri
    '''
    Key = Key
    def init(self, ns=None, id=None):
        self.ns = ns
        self.id = id
        super().init(Key.Pub)
    def set_id(self, id):
        self.id = id
    def call(self, *a,**b):
        return self.tget(*a,**b)
    @staticmethod
    def nsid(src, id):
        if isinstance(src, TagData):
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
