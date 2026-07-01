
from .apis.apis import api_build
from buildz.base import Base
from buildz import xf, fz, dz
from buildz import log as logz
from .struct import *
from . import tlx


class SimpleAgent(Base):
    '''
        封装对openai和ollama接口的调用，封装成一样的接口
    '''
    @staticmethod
    def build_conf(conf, log=None, tools=None):
        interface = conf.get("interface", "openai")
        url = conf.get("url")
        api_key = conf.get("api_key")
        send_conf= conf.get("send")
        if 'log' in conf and log is None:
            log = logz.build_conf(conf.get("log"), {})
        return SimpleAgent(interface, url, api_key, send_conf, log, tools)
    def init(self, interface, url, api_key=None, send_conf = {}, log=None, tools=None):
        log = log or logz.simple()
        self.log = log("api.client")
        self.interface = interface
        self.send_conf=send_conf
        self.client=api_build(interface, url, api_key, self.log)
        self.tools = tools or tlx.Tools(log)
    def embed(self, msg:str, model:str=None)->list[float]:
        model = model or self.send_conf.get("embed_model")
        return self.client.embed(msg, model)
    def get_tools(self):
        return self.tools
    def new_send(self, put_tools=True):
        send = Send.from_conf(self.send_conf)
        if put_tools:
            send.tools = self.tools.out()
        return send
    def send(self, send):
        #self.log.debug("send:", send)
        msg, usage = self.client.send(send)
        #self.log.debug("recv:", msg)
        #exit()
        return msg, usage
    def simple(self, **maps):
        return self.send(**maps)[0]
    def lsimple(self, send, tools=None):
        tools = tools or self.tools
        while True:
            rst, usage=self.send(send)
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

