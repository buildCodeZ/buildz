from ..base import Base
class Lists(Base):
    def init(self, *keys):
        self.lists = {}
        for k in keys:
            self.lists[k] = []
        self.enables = set()
    def add(self, kid, _type, fc, enable=True):
        if _type:
            if _type not in self.lists:
                self.lists[_type] = []
            self.lists[_type].append([kid, fc])
        else:
            for _type in slef.lists.keys():
                self.lists[_type].append([kid, fc])
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
        for kid, fc in self.lists[_type]:
            if kid not in self.enables:
                continue
            data = fc(data, *a, **b)
        return data
    def __getattr__(self, key):
        if key in {'lists', 'enables'}:
            return super().__getattr__(key)
        def fc(data, *a, **b):
            return self.call(key, data, *a, **b)
        return fc


    

