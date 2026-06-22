
from buildz.base import Base
from buildz import xf, fz, dz
from ..api import Api

class OllamaApi(Api):
    @staticmethod
    def from_conf(conf):
        return OllamaApi(conf.get("url"))
    def init(self, url, api_key=None):
        import ollama 
        self.url = url
        self.client = ollama.Client(url)
    def send_dict(self, send:dict)->tuple[dict, dict]:
        rsp = self.client.chat(**send)
        usage =dz.maps(
            send = rsp.prompt_eval_count,
            recv = rsp.eval_count
        )
        usage['total'] = usage['send']+usage['recv']
        msg = rsp.message
        rst = dz.maps(role=msg.role, content=msg.content, think=msg.thinking, tool_calls=msg.tool_calls)
        return rst, usage
