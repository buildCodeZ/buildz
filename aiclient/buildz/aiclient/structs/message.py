

from typing import List, Dict, Any, Optional
from buildz.base import Base
from buildz import log as logz, dz, xf
import json
class Message(Base):
    '''
        单条消息，包括：
        content: 消息内容
        role: 消息角色，默认'user'也就是用户
        tool_call_id: 技能调用id，用在api返回说要调用技能，本机调用技能后返回技能调用结果，会带上该id
            该字段有些别扭，后续openapi等接口可能会进行修改
    '''
    def clone(self):
        return Message(self.content, self.role, self.tool_call_id)
    def init(self, content, role='user', tool_call_id=None):
        self.content = content
        self.role = role
        self.tool_call_id=tool_call_id
    def size(self):
        rst = self.out()
        rs = json.dumps(rst)
        return len(rs)//4
    def out_text(self):
        content = json.dumps([self.content], ensure_ascii=False)[1:-1]
        s = f"role: {self.role}\ncontent :{content}\n"
        if self.tool_call_id:
            s+=f"tool_call_id :self.tool_call_id\n"
        return s
    def out_xml(self):
        s = f"<role>{self.role}</role><content>{self.content}</content>"
        if self.tool_call_id:
            s+=f"<tool_call_id>{self.tool_call_id}</tool_call_id>"
        return s
    def str(self):
        return self.out_xml()
    def out_json(self):
        return self.out()
    def out(self):
        rst = {}
        rst = dz.snn(rst, role=self.role, content=self.content, tool_call_id =self.tool_call_id)
        return rst
    @staticmethod
    def from_conf(conf):
        content, role, tool_call_id = dz.g(conf, content=None, role=None, tool_call_id=None)
        return Message(content, role, tool_call_id)
