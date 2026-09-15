
from typing import List, Dict, Any, Optional
import json
from buildz.base import Base
from buildz import log as logz, dz, xf
from .toolcall import ToolCall
class Recv(Base):
    '''
        api返回数据，包括字段：
        role: 回答问题的角色
        content: 回答的文字
        think: 思考的文字
        tool_calls: 调用的技能列表
    '''
    @staticmethod
    def from_conf(conf):
        role, content, think, tools = dz.g(conf, role=None, content=None, thinkg=None, tool_calls=None)
        if tools:
            tools = [ToolCall.from_conf(k) for k in tools ]
        return Recv(role, content, think, tools)
    def tool_calls_out(self, tools):
        if self.tool_calls is None:
            return None
        rst = [tcall(tools) for tcall in self.tool_calls]
        return rst
    def str(self):
        rst = dz.mapsnn(role=self.role, content=self.content, think=self.think, tool_calls=self.tool_calls)
        return str(rst)
    def init(self, role, content, think, tool_calls):
        self.role = role
        self.content= content
        self.think = think
        self.tool_calls = tool_calls
    def clone(self):
        return Recv(self.role, self.content, self.think, self.tool_calls)
    def out_tool_calls(self):
        if self.tool_calls is None:
            return None
        return [tl.out() for tl in self.tool_calls]
    def out_tool_calls_json(self):
        if self.tool_calls is None:
            return None
        return [tl.out_json() for tl in self.tool_calls]
    def size(self):
        rst = self.out()
        rs = json.dumps(rst)
        return len(rs)//4
    def out(self):
        rst = dz.mnn(role=self.role, content=self.content, tool_calls=self.out_tool_calls(), think=self.think)
        return rst
    def out_json(self):
        rst = dz.mnn(role=self.role, content=self.content, tool_calls=self.out_tool_calls_json())
        return rst
    def out_xml(self):
        s = f"<role>{self.role}</role>"
        if self.content:
            s+=f"<content>{self.content}</content>"
        if self.tool_calls:
            arr = [f"<tool_call>{tcall.out_xml()}</tool_call>" for tcall in self.tool_calls]
            rs = "".join(arr)
            s += f"<tool_calls>{rs}</tool_calls>"
        return s

