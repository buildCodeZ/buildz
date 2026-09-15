

from .datas import Datas
from .memory import Memory
__doc__="""
Memories

"""

class Memories(Datas):
    def init(self, do_json=True):
        super().init(Memory.from_json, do_json, "memories")
    def search_subject(self, subject):
        '''
            查找所有主体是subject的数据
        '''
        rst = self._search('subject', subject)
        return rst
    def search_object(self, object):
        rst = self._search('object', object)
        return rst
    def search_near(self, num=10):
        '''
            返回最近num条记忆
        '''
        return self.datas[-num:]
