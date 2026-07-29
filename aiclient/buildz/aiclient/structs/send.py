
from buildz.base import Base
from buildz import log as logz, dz, xf
from .message import Message
from typing import List, Dict, Any, Optional
class Send(Base):
    '''
       发送报文的结构化对象体 
       messages: Message的列表，默认空
       tools: 
    '''
    def str(self):
        return str(self.out())
    def init(self, messages:List[Message]=None, tools:List[Dict]=None, tool_choice:str="auto", model:str=None,think=True, stop=None, max_tokens=None):
        messages = messages or []
        self.model = model
        self.think = think
        self.messages=messages
        self.tools = tools
        self.tool_choice = tool_choice
        self.stop = stop
        self.max_tokens = max_tokens
    def clean(self):
        self.messages = []
        return self
    def adds(self, msgs):
        self.messages += msgs
    def addx(self, **maps):
        msg = Message(**maps)
        self.messages.append(msg)
        return msg
    def add(self, msg):
        if type(msg)==str:
            msg = Message(msg)
        self.messages.append(msg)
        return msg
    def out(self, send_tools=True):
        rst = {}
        msgs = self.messages
        if msgs:
            msgs = [msg.out() if isinstance(msg, Message) else msg for msg in msgs]
        rst = dz.snn(rst, model=self.model, messages=msgs, think=self.think, stop=self.stop, max_tokens=self.max_tokens)
        if send_tools:
            rst = dz.snn(rst, tools=self.tools, tool_choice=self.tool_choice)
        return rst
    @staticmethod
    def from_conf(conf:dict):
        messages, tools, tool_choice, model, think, stop, max_tokens = dz.g(conf, messages=None, tools=None, tool_choice="auto", model=None, think=None, stop=None, max_tokens=None)
        if messages:
            messages = [Message.from_conf(msg) for msg in messages]
        return Send(messages, tools, tool_choice, model, think=think, stop=stop, max_tokens=max_tokens)
pass
