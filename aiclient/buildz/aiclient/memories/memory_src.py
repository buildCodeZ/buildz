

import json, time, os
from buildz.base import Base
from buildz.html import base as xml
from buildz import xf,dz,fz, log as logz, path as pathz
pth = pathz.Path(os.path.dirname(__file__))
class Data(Base):
    _data_ks = []
    _match_ks = None
    def str(self):
        return self.out_xml()
    def init(self, *args, **kwargs):
        for i in range(min(len(args), len(self._data_ks))):
            k = self._data_ks[i]
            v = args[i]
            setattr(self, k, v)
        for k in self._data_ks:
            if k in kwargs:
                setattr(self, k, kwargs[k])
        #for k,v in kv.items():
        #    setattr(self, k, v)
        #self._data_ks = list(kv.keys())
        #self._match_ks = list(self._data_ks)
    def out(self, abs=None):
        if abs is None:
            abs = set()
        elif type(abs)==str:
            abs = [abs]
        abs = set(abs)
        rst = {}
        for k in self._data_ks:
            if k in abs:
                continue
            rst[k] = getattr(self, k)
        return rst
    def out_xml(self, abs=None):
        rst = self.out(abs)
        s = xml.xr(**rst)
        return s
    def out_json(self, abs=None):
        rst = self.out(abs)
        s = dz.jnn(**rst)
        return s
    def match(self, obj):
        ks = self._match_ks or self._data_ks
        for k in ks:
            if getattr(self, k)!=getattr(obj, k):
                return False
        return True
    @staticmethod
    def from_json(obj, cls, ks=None):
        ks = ks or cls._data_ks
        rst = dz.lgets(obj, ks)
        return cls(*rst)
    @staticmethod
    def from_xml(obj, cls, ks=None):
        ks = ks or cls._data_ks
        rst = {}
        for key in ks:
            dts = obj.tags(key)
            if len(dts)>0:
                rst[key] = dts[0].text
            else:
                rst[key] = None
        return cls(**rst)
    @staticmethod
    def from_obj(obj, cls):
        if isinstance(obj, xml.HtmlTag):
            return cls.from_xml(obj)
        else:
            return cls.from_json(obj)
    @staticmethod
    def wrap_from(cls):
        def from_json(obj):
            return Data.from_json(obj, cls)
        def from_xml(obj):
            return Data.from_xml(obj, cls)
        def from_obj(obj):
            return Data.from_obj(obj, cls)
        cls.from_json = staticmethod(from_json)
        cls.from_xml= staticmethod(from_xml)
        cls.from_obj = staticmethod(from_obj)
        return cls



@Data.wrap_from
class Relation(Data):
    _data_ks = "date,key,content".split(",")
@Data.wrap_from
class Memory(Data):
    _data_ks = "date,subject,object,relation,content".split(",")
class Datas(Base):
    format="%Y-%m-%d %H:%M:%S"
    def str(self):
        return f"<Datas>"+self.build_xml()+"</Datas>"
    def sec2date(self, sec=None):
        sec = sec or time.time()
        return time.strftime(self.format, time.localtime(sec))
    def date2sec(self, date):
        assert False, 'not impl'
    def init(self, tag, do_json, data_from_json):
        self.do_json = do_json
        self.data_from_json = data_from_json
        self.tag = tag
        self.datas = []
    def build_json(self, abs=None):
        datas = [self.wrap_json(dt.out_json(abs)) for dt in self.datas]
        return datas
    def build_xml(self, abs=None):
        datas = [self.wrap_xml(self.tag, dt.out_xml(abs)) for dt in self.datas]
        datas = "".join(datas)
        return datas
    def wrap_json(self, obj, sec=None):
        if sec:
            date = self.sec2date(sec)
            obj['date'] = date
        return obj
    def wrap_xml(self, tag, s, sec=None):
        if sec:
            date = self.sec2date(sec)
            s = s+xml.xr(date=date)
        return xml.w(tag, s)
    def work(self, obj):
        '''
            获取增删改数据，做增删改
        '''
        out_rps, out_incs, out_dels = [],[],[]
        if self.do_json:
            incs, dels, rps = dz.g(obj, increments=[], removes=[], replaces = [])
        else:
            incs = xml.arr(obj, "increments", "increment")
            dels = xml.arr(obj, "removes", "remove")
            rps = xml.arr(obj, "replaces", "replace")
        def clean(arr):
            return [k for k in arr if k is not None]
        for rp in rps:
            out_rps+=clean([self.do_replace(rp)])
        for inc in incs:
            out_incs+=clean([self.do_inc(inc)])
        for rm in dels:
            out_dels += clean([self.do_del(rm)])
        return out_rps, out_incs, out_dels
    def find(self, obj):
        for i in range(len(self.datas)):
            if self.datas[i].match(obj):
                return i
        return -1
    def do_del(self, rm):
        rm = xml.x2j(rm)
        dt = self.data_from_json(rm)
        find = self.find(dt)
        if find<0:
            print(f"error do del on {rm}: not found")
            return None
        assert find>=0
        return self.datas.pop(find)
    def do_inc(self, inc):
        inc = xml.x2j(inc)
        dt = self.data_from_json(inc)
        dt.date = self.sec2date()
        self.datas.append(dt)
        return dt
    def do_replace(self, rp):
        rp = xml.x2j(rp)
        src = rp.get("source", {})
        rpl = rp.get("target", {})
        src = self.data_from_json(src)
        rpl = self.data_from_json(rpl)
        rpl.date = self.sec2date()
        find = self.find(src)
        if find<0:
            print(f"error do replace on {rp}: not found")
            return None
        assert find>=0
        self.datas[find] = rpl
        return rpl
class Memories(Datas):
    '''
        模拟代理记忆
        规则：
            对话不超过max个字符串的部分直接使用
            超过的部分提取记忆
            提取方式：
                最少提取n条
                每条对话搜索记忆中符合的记忆项
                记忆项列表+需要提取记忆的对话发agent
                要求agent返回：
                    需要替换的记忆，新增的记忆
                新增的记忆查符合的记忆项发agent
                要求agent返回：
                    是否存在替换，替换哪条记忆
                基础版里不做搜索，所有记忆都发agent，也就不用第二次发送了
            发送agent的时候会带上记忆方式：
                当前对话提取的记忆全部带上，其他记忆计算关联性（向量计算），提取关联度最高的
        
    '''
    def str(self):
        datas = [x.out_xml() for x in self.datas]
        datas = "\n".join(datas)
        s = f"Mem[[\n{datas}\n]]"
        return s
    def init(self, agent, rls=None, log=None, do_json=False):
        super().init("memory", do_json, Memory.from_json)
        rls = rls or Datas("relation", do_json, Relation.from_json)
        log = log or logz.simple()
        self.log = log.sub("memory")
        self.rls = rls
        self.agent = agent
        self.send = agent.new_send()
        fp = "memory_xml.txt" if not do_json else "memory_json.txt"
        self.system_msg = fz.read(pth(fp)).decode("utf-8")
    def new_send(self, msg):
        self.send.clean()
        self.send.addx(role="system", content=self.system_msg)
        self.send.add(msg)
        return self.send
    def build_json(self, msgs, abs=None):
        rls = self.rls.build_json()
        chats = [self.wrap_json(msg.out_json(), sec) for msg, sec in msgs]
        mems = super().build_json(abs=abs)
        return chats, mems, rls
    def build_xml(self, msgs, abs=None):
        rls = self.rls.build_xml()
        chats = [self.wrap_xml("chat", msg.out_xml(), sec) for msg,sec in msgs]
        chats = "".join(chats)
        mems =super().build_xml(abs=abs)
        return chats, mems, rls
    def do_mem(self, msgs, mems = []):
        if self.do_json:
            chats, mems, rls= self.build_json(msgs)
            send = dz.jnn(relations=rls, memories=mems, chats=chats)
        else:
            chats, mems, rls = self.build_xml(msgs)
            send = xml.xr(relations=rls, memories=mems, chats=chats)
        send = self.new_send(send)
        recv, usage = self.agent.send(send)
        content = recv.content
        self.log.info(f"memory out: {content}")
        if content[0]=="<":
            obj = xml.parse(content)
            rls = obj.tags("relations")[0]
            mems = obj.tags("memories")[0]
        else:
            obj = json.loads(content)
            mems = obj.get("memories", {})
            rls = obj.get("relations", {})
        self.rls.work(rls)
        rpls, incs, dels = self.work(mems)
        return rpls+incs


class Client(Base):
    '''
        需要生成记忆的策略：
            n次调用后
            超过字数限制后

            mem: 记忆对象
            token_size: 消息队列token数大于该最大值后触发记忆
            times_mem: 新增多少消息后触发记忆
            fetch_num: 每次调用记忆，存储多少条消息
            history_mem: 最新的多少条记忆直接发
    '''
    def init(self, mems, token_size=40960, fetch_num=1, times_mem=-1, history_mem=3, log=None, do_json=False):
        log=log or logz.simple()
        self.log=log.sub("memory_client")
        self.mems = mems
        self.msgs = []
        self.history = []
        self.token_size = token_size
        self.fetch_num = fetch_num
        self.times_mem = times_mem
        self.history_mem = history_mem
        self.msg_used = 0
        self.count = 0
        self.do_json = do_json
    def do_mem(self):
        self.log.debug("client do mem")
        outs = []
        for i in range(self.fetch_num):
            if len(self.msgs)==0:
                break
            msg, sec = self.msgs.pop(0)
            outs.append([msg, sec])
            self.msg_used -= msg.size()
        self.history+=self.mems.do_mem(outs, self.history)
        if len(self.history)>self.history_mem:
            self.history = self.history[-self.history_mem:]
    def add(self, msg):
        msg = msg.clone()
        size = msg.size()
        #self.log.debug(f"mem_cli add msg: {msg}")
        self.msgs.append([msg, time.time()])
        self.count+=1
        self.msg_used+=size
        self.log.debug(f"msg_used after add: {self.msg_used}/{self.token_size}")
        if self.times_mem>0 and self.count>=self.times_mem:
            self.do_mem()
            self.count=0
        while self.msg_used>=self.token_size:
            self.do_mem()
    def build_msg(self, msg):
        if self.do_json:
            chats, mems, rls = self.mems.build_json(self.msgs, abs="relation")
            msg = dz.mnn(date=self.mems.sec2date(), content=msg)
            send = dz.jnn(memories=mems, chats=chats, quest=msg)
        else:
            chats, mems, rls = self.mems.build_xml(self.msgs, abs="relation")
            msg = xml.xr(date=self.mems.sec2date(), content=msg)
            send = xml.xr(memories=mems, chats=chats, quest=msg)
        return send
    def save(self):
        while len(self.msgs)>0:
            self.do_mem()
        self.log.info(f"done record all msgs to mem: {self.mems}")
