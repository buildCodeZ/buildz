from ..base import Base
'''
包含三个类，功能都是把一个列表的方法封装成一个方法，调用该方法的时候，实际会顺序调用列表里的所有方法
List:
    存储一个列表，调用该List的__call__就是顺序调用列表
    添加方法是add(obj, index=None): index是插入位置，默认插入队列末尾，调用后返回插入凭证ind，可以用该ind把数据从列表里删除
    删除方法有两个,一个是remove(ind)：输入add返回的ind，返回被删除的obj
                一个是remove_obj(obj): 输入的是add里放的obj，通过判断列表里obj_i==obj找到数据并删除，返回bool，True是删除成功，False是删除失败（没找到）
    示例:
        obj=List()
        obj.add(lambda x:x+1)
        obj.add(lambda x:x*2)
        ind = obj.add(lambda x:x-10)
        print(obj(10))
        # 12
        obj.remove(ind)
        print(obj(10))
        # 22

Lists:
    逻辑相对复杂，不只是多个方法列表，还多了标签是否启动的设置，往方法列表插入方法，要设置该方法对应的标签
    可以设置标签是否使用，如果不使用，标签对应的方法就不会调用
    其实应该先写一个简单不含标签的，再继承写一个含标签的
    Lists开发是为了方便对称方法的配置
    示例:
        # Lists创建的时候可以配置某个方法是顺序还是倒叙插入,1是顺序，-1是倒叙
        # 假设需要一个send方法和一个recv方法，配置如下:
        # send方法列表顺序插入列表方法，recv方法列表倒叙插入方法列表
        # 方法列表都是顺序调用
        obj = Lists(send=1, recv=-1)
        # 添加字符串转字节码的方法
        # 可以add分别添加，也可以adds一次添加
        # 如果某个处理逻辑只在send或recv的时候需要，也可以只add添加send或recv
        obj.add('tobytes', 'send', lambda x:x.encode('utf-8'))
        obj.add('tobytes', 'recv', lambda x:x.decode('utf-8'))
        # 添加加密解密方法
        obj.adds('crypt', send=fc_encrypt, recv=fc_decrypt)
        # send添加个打印输出的方法
        def disp(x):
            print(x)
            return x
        obj.adds('show', send = disp)
        x = 'test'
        x2send = obj.send(x)
        # 这里因为添加了disp，会打印加密后的数据
        # x2send = b'加密后数据'
        xrecv = obj.recv(x2send)
        # xrecv = 'test'
        # 禁用标签crypt对应的方法
        obj.disable('crypt')
        x = 'test'
        x2send = obj.send(x)
        # 这里因为添加了disp，会打印x对应的字节码
        # x2send = b'test'
        xrecv = obj.recv(x2send)
        # xrecv = 'test'

'''
class List(Base):
    def init(self, out_as_in=True, add_last=True):
        self.datas = []
        self.index=0
        self.out_as_in = out_as_in
        self.add_last=add_last
    def add(self, obj, index=None):
        ind = self.index
        self.index+=1
        if index is None:
            if self.add_last:
                self.datas.append((ind, obj))
            else:
                self.datas.insert(0, (ind, obj))
        else:
            self.datas.insert(index, (ind, obj))
        return ind
    def remove(self, ind):
        find=-1
        for i in range(len(self.datas)):
            if self.datas[i][0]==ind:
                find=i
                break
        if find:
            return self.datas.pop(find)[1]
        return None
    def remove_obj(self, obj):
        find = -1
        for i in range(len(self.datas)):
            if self.datas[i][1]==obj:
                find=i
                break
        if find:
            self.datas.pop(find)[1]
            return True
        return False
    def deal_obj(self, obj, *args, **kwargs):
        for ind, deal in self.datas:
            obj = deal(obj, *args, **kwargs)
        return obj
    def deal_nobj(self, *args, **kwargs):
        rst = None
        for ind, deal in self.datas:
            rst = deal(*args, **kwargs)
        return rst
    def call(self, *args, **maps):
        if self.out_as_in:
            return self.deal_obj(*args, **maps)
        else:
            return self.deal_nobj(*args, **maps)
pass
class ListDeal(List):
    def init(self, out_as_in=False):
        super().init(out_as_in)
pass
class Lists(Base):
    '''
        Lists(**maps)
        example:
            fcs = Lists(send=-1, recv=1)
            fcs.adds("encrypt", 'send', fc_encrypt)
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


    
