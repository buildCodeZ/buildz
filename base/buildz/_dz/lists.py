from ..base import Base
class Lists(Base):
    '''
        Lists(**maps)
        example:
            fcs = Lists(send=-1, recv=1)
            fcs.adds("encrypt", True, send=fc_encrypt, recv=fc_decrypt)
            fcs.add("json", True, send = json.dumps, recv = json.loads)
            data = {"test": 123}
            data = fcs.send(data) 
            # {"test":123} => '{"test":123}' => crypt_data
            data = fcs.recv(data)
            # crypt_data => '{...}' => {...}
        key=1:
            add的时候加到调用队列的末尾（越后面添加调用顺序越靠后）
        key=-1:
            add的时候加到调用队列的开头（越后面添加调用顺序越靠前）
        call(key, dt, *a, **b):
            for fc in self.fcss[key]:
                dt = fc(dt, *a, **b)
            return dt
    '''
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


    

