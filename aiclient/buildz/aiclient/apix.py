
from buildz.base import Base
from buildz import log as logz, dz, xf
import openai 
import ollama 
from os.path import dirname, join
dp = dirname(__file__)
global_conf = xf.loadf(join(dp, "argx.js"))

class Client(Base):
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
        return Client(interface, url, api_key, base_conf, fetch, log)
    def init(self, interface, url, api_key, base_conf = {}, fetchs={}, log=None):
        log = log or logz.simple()
        self.log = log("api.client")
        self.interface = interface
        self.fetchs = fetchs
        if interface=='ollama':
            self._send = self.send_ollama
            cli = ollama.Client(url)
        else:
            self._send = self.send_openai
            cli = openai.OpenAI(base_url = url, api_key = api_key)
        self.base_conf = base_conf
        self.url = url
        self.client=cli
    def fetch(self, msg):
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
    def send(self, **maps):
        if self.base_conf and len(self.base_conf)>0:
            conf = {}
            conf.update(self.base_conf)
            conf.update(maps)
        else:
            conf = maps
        self.log.info(f"send: ({self.interface})'{self.url}', json: {conf}")
        rp, usage = self._send(**conf)
        self.log.info(f"rsp: {rp}, usage: {usage}")
        return rp, usage
    def simple(self, **maps):
        return self.send(**maps)[0]

pass

