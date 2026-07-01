
from typing import List, Dict, Any, Optional

from buildz.base import Base
from buildz import log as logz, dz, xf
import json
class ToolCall(Base):
    '''
        工具调用对象转化的结构化对象，解析其他库调用模型后获取的工具调用对象，转换成本工具调用对象，方便不同模型库的调用处理
    '''
    def str(self):
        rst = dz.mapsnn(id=self.id, fn=self.fn, args=self.args, type="tool_call")
        return str(rst)
    def init(self, id, fn, args, role='tool'):
        self.id=id
        self.fn = fn
        self.args=args
        self.role =role
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
        #rst = {'id': self.id, 'function': {'name':self.fn, 'arguments': json.dumps(self.args)}}
        rst = {'id': self.id, 'function': {'name':self.fn, 'arguments': self.args}}
        return rst
    @staticmethod
    def from_conf(conf):
        id,role, fc=dz.g(conf,id=None,role='tool', function={})
        fn, args=dz.g(fc, name=None, arguments={})
        return ToolCall(id,fn,args,role)
