
from typing import List, Dict, Any, Optional

from buildz.base import Base
from buildz import log as logz, dz, xf
from .toolcall import ToolCall
class Recv(Base):
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
    def out_tool_calls(self):
        if self.tool_calls is None:
            return None
        return [tl.out() for tl in self.tool_calls]
    def out(self):
        rst = {'role':self.role, 'content':self.content, 'tool_calls':self.out_tool_calls()}
        return rst

