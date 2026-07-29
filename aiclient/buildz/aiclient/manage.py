
import json, time, os
from buildz.base import Base
from buildz.html import base as xml
from buildz import xf,dz,fz, log as logz, path as pathz
pth = pathz.Path(os.path.dirname(__file__))
from . import agent as agentz
from . import memory as memoryz
from . import struct as structz

'''
输入输出做封装：

调用ai前，加上历史记录（短期记忆），长期记忆，相关向量记忆

调用ai后，对返回处理：
加入历史记录，历史记录过长，

调用ai，抽取关系联系（A，B，关系）
关系存图里


'''

class Manager(Base):
    def init(self, agent, log=None, do_json=False):
        log = log or logz.simple()
        self.mems = memoryz.Memories(agent, log=log, do_json = do_json)
        self.client = memoryz.Client(self.mems, token_size=4096, fetch_num=3, times_mem=10, log=log, do_json = do_json)
        self.agent = agent
        fp = "manage_xml.txt" if not do_json else "manage_json.txt"
        self.system_msg = fz.read(pth(fp)).decode("utf-8")
        self.log = log
    def chat(self, msg):
        src = structz.Message(msg)
        msg = self.client.build_msg(msg)
        send = self.agent.new_send()
        send.clean()
        send.addx(role="system", content=self.system_msg)
        umsg = send.add(msg)
        self.client.add(src)
        recv, usage = self.agent.send(send)
        content = recv.content
        self.client.add(recv)
        return content
    def save(self):
        self.client.save()
    def test_chat(self, send, recv):
        src = structz.Message(**send)
        recv = structz.Message(**recv)
        self.client.add(src)
        self.log.info(f"his user: {src.content}")
        time.sleep(1)
        self.client.add(recv)
        self.log.info(f"his agent: {recv.content}")
        time.sleep(1)


