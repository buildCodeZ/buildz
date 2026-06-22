
from buildz.base import Base
from buildz import log as logz, dz, xf
import openai 
import ollama 
import json
from os.path import dirname, join
from . import tlx
from typing import List, Dict, Any, Optional
dp = dirname(__file__)
global_conf = xf.loadf(join(dp, "argx.js"))
def simple_out(obj):
    return obj.out()
class Send(Base):
    '''
       发送报文的结构化对象体 
       messages: Message的列表，默认空
       tools: 
    '''
    def str(self):
        return str(self.out())
    def init(self, messages:List[Message]=None, tools:List[Dict]=None, tool_choice:str="auto", model:str=None, send_tools:bool=True):
        messages = messages or []
        self.model = model
        self.messages=messages
        self.tools = tools
        self.tool_choice = tool_choice
        self.send_tools=send_tools
    def call(self, send_tools=True):
        self.send_tools=send_tools
        return self
    def adds(self, msgs):
        self.messages += msgs
    def add(self, msg):
        if type(msg)==str:
            msg = Message(msg)
        self.messages.append(msg)
    def out(self, send_tools=None):
        if send_tools is None:
            send_tools = self.send_tools
        rst = {}
        msgs = self.messages
        if msgs:
            msgs = [msg.out() if isinstance(msg, Message) else msg for msg in msgs]
        rst = dz.snn(rst, model=self.model, messages=msgs)
        if send_tools:
            rst = dz.snn(rst, tools=self.tools, tool_choice=self.tool_choice)
        return rst
pass
class Message(Base):
    def init(self, content, role='user', tool_call_id=None):
        self.content = content
        self.role = role
        self.tool_call_id=tool_call_id
    def out(self):
        rst = {}
        rst = dz.snn(rst, role=self.role, content=self.content, tool_call_id =self.tool_call_id)
        return rst
class ToolCall(Base):
    '''
        工具调用对象转化的结构化对象，解析其他库调用模型后获取的工具调用对象，转换成本工具调用对象，方便不同模型库的调用处理
    '''
    def str(self):
        rst = dz.mapsnn(id=self.id, fn=self.fn, args=self.args, type="tool_call")
        return str(rst)
    def init(self, toolcall, role='tool'):
        self.id = toolcall.id
        self.fn = toolcall.function.name
        self.role = role
        self.args = json.loads(toolcall.function.arguments)
    def call(self, tools, role=None):
        '''
            进行实际工具调用
        '''
        role = role or self.role
        rst = tools.call(self.fn, self.args)
        rst = {'role':role, "tool_call_id":self.id, "content":str(rst)}
        return rst
    def msg(self, tools):
        '''
            进行实际工具调用，并返回Message
        '''
        rst = self.call(tools)
        return Message(rst, 'tool', self.id)
    def out(self):
        '''
            结构体对象重组成json报文
        '''
        rst = {'id': self.id, 'function': {'name':self.fn, 'arguments': json.dumps(self.args)}}
        return rst
class Recv(Base):
    def tool_calls_out(self, tools):
        if self.tool_calls is None:
            return None
        rst = [tcall(tools) for tcall in self.tool_calls]
        return rst
    def str(self):
        rst = dz.mapsnn(role=self.role, content=self.content, think=self.think, tool_calls=self.tool_calls)
        return str(rst)
    def init(self, maps):
        self.cache = maps
        self.role = dz.g(maps, role=None)
        self.content= dz.g(maps, content=None)
        self.think = dz.g(maps, think=None)
        tools =dz.g(maps, tool_calls=None)
        if tools:
            tools = [ToolCall(k) for k in tools if k.type=='function']
        self.tool_calls = tools
    def out_tool_calls(self):
        if self.tool_calls is None:
            return None
        return [tl.out() for tl in self.tool_calls]
    def out(self):
        rst = {'role':self.role, 'content':self.content, 'tool_calls':self.out_tool_calls()}
        return rst

class Client(Base):
    '''
        封装对openai和ollama接口的调用，封装成一样的接口
    '''
    @staticmethod
    def build(conf, log=None):
        x = {}
        x.update(global_conf)
        x.update(conf)
        conf=x
        interface = conf.get("interface", "openai")
        url = conf.get("url")
        api_key = conf.get("api_key")
        base_conf = conf.get("conf")
        fetchs = conf.get("fetchs")
        fetch = fetchs.get(interface, fetchs.get("openai"))
        sends = conf.get("sends")
        send = sends.get(interface, fetchs.get("openai", {}))
        return Client(interface, url, api_key, base_conf, fetch, send, log)
    def init(self, interface, url, api_key, base_conf = {}, fetchs={}, sends={}, log=None):
        log = log or logz.simple()
        self.log = log("api.client")
        self.interface = interface
        self.fetchs = fetchs
        self.sends=sends
        if interface=='ollama':
            self._send = self.send_ollama
            cli = ollama.Client(url)
        else:
            self._send = self.send_openai
            cli = openai.OpenAI(base_url = url, api_key = api_key)
        self.base_conf = base_conf
        self.url = url
        self.client=cli
    def fetch_send(self, msg):
        '''
            发送模型的字段做转换，转换成模型接口库的格式
        '''
        rst = {}
        msg = dz.deep_fill(msg, rst)
        #print(f"msg: {msg}")
        for k,v in self.sends.items():
            ks=k.split(".")
            vs=v.split(".")
            #print(f"ks: {ks}, vs: {vs}")
            if not dz.dhas(msg, vs):
                continue
            val = dz.dget(msg, vs)
            dz.dremove(msg, vs)
            dz.dset(msg, ks, val)
        return msg
    def fetch(self, msg):
        '''
            模型返回的字段做转化，转化成本代码库的格式
        '''
        rst = {}
        for k,v in self.fetchs.items():
            dt = getattr(msg, v, None)
            rst[k] = dt
        return rst
    def send_openai(self, **send):
        rsp = self.client.chat.completions.create(**send)
        message = rsp.choices[0].message
        usage = rsp.usage
        usage =dz.maps(
            total = usage.total_tokens,
            send = usage.prompt_tokens,
            recv = usage.completion_tokens
        )
        rst = self.fetch(message)
        return rst, usage
    def send_ollama(self, **send):
        rsp = self.client.chat(**send)
        usage =dz.maps(
            send = rsp.prompt_eval_count,
            recv = rsp.eval_count
        )
        usage['total'] = usage['send']+usage['recv']
        message = rsp.message
        rst = self.fetch(message)
        return rst, usage
    def send(self, *args, **maps):
        if len(args)==1 and isinstance(args[0], Send):
            tmp = args[0].out()
            dz.deep_fill(maps, tmp)
            maps = tmp
        if self.base_conf and len(self.base_conf)>0:
            conf = {}
            conf.update(self.base_conf)
            conf.update(maps)
        else:
            conf = maps
        conf = self.fetch_send(conf)
        self.log.info(f"send: ({self.interface})'{self.url}', json: {conf}")
        rp, usage = self._send(**conf)
        self.log.info(f"rsp: {rp}, usage: {usage}")
        return rp, usage
    def simple(self, **maps):
        return self.send(**maps)[0]
    def wsimple(self, send):
        rst, usage = self.send(send)
        rst = Recv(rst)
        return rst
    def lsimple(self, send, tools):
        while True:
            rst, usage=self.send(send)
            rst = Recv(rst)
            send.add(rst.out())
            tool_calls = rst.tool_calls
            if tool_calls is None or len(tool_calls)==0:
                break
            tls = rst.tool_calls_out(tools)
            if tls:
                for tl in tls:
                    send.add(tl)
        return rst


pass

