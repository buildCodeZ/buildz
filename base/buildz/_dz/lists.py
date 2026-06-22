from ..base import Base
class Lists(Base):
    def init(self, *keys, **maps):
        self.lists = {}
        self.orders = {}
        for k in keys:
            self.lists[k] = []
            self.orders[k]=1
        for k,v in maps.items():
            self.lists[k]=[]
            self.orders[k] = v
        self.enables = set()
    def add_lists(self, _type, obj):
        if self.orders[_type]>0:
            self.lists[_type].append(obj)
        else:
            self.lists[_type].insert(0, obj)
    def add(self, kid, _type, fc, enable=True):
        if _type:
            if _type not in self.lists:
                self.lists[_type] = []
                self.orders[_type] = 1
            self.add_lists(_type, [kid, fc])
        else:
            for _type in self.lists.keys():
                self.add_lists(_type, [kid, fc])
        self.enable(kid, enable)
    def adds(self, kid, enable, **maps):
        for _type, fc in maps.items():
            self.add(kid, _type, fc, enable)
    def enable(self, kid, val=True):
        if val:
            self.enables.add(kid)
        elif kid in self.enables:
            self.enables.remove(kid)
    def disable(self, kid):
        return self.enable(kid, False)
    def call(self, _type, data, *a, **b):
        #print(f"list.call start")
        for kid, fc in self.lists[_type]:
            if kid not in self.enables:
                continue
            #print(f"list.call before {fc}")
            data = fc(data, *a, **b)
            #print(f"list.call after {fc}")
        #print(f"list.call done")
        return data
    def __getattr__(self, key):
        if key in {'lists', 'enables'}:
            return super().__getattr__(key)
        def fc(data, *a, **b):
            return self.call(key, data, *a, **b)
        return fc


    

