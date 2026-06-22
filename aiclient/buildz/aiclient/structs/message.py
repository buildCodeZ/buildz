

from typing import List, Dict, Any, Optional
from buildz.base import Base
from buildz import log as logz, dz, xf

class Message(Base):
    def init(self, content, role='user', tool_call_id=None):
        self.content = content
        self.role = role
        self.tool_call_id=tool_call_id
    def out(self):
        rst = {}
        rst = dz.snn(rst, role=self.role, content=self.content, tool_call_id =self.tool_call_id)
        return rst
    @staticmethod
    def from_conf(conf):
        content, role, tool_call_id = dz.g(conf, content=None, role=None, tool_call_id=None)
        return Message(content, role, tool_call_id)
