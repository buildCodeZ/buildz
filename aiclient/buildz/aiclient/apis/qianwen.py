
from buildz.base import Base
from buildz import xf, fz, dz
from ..api import Api
from .openai import OpenAiApi
class QianwenApi(OpenAiApi):
    @staticmethod
    def from_conf(conf):
        return QianwenApi(conf.get("url"), conf.get("api_key"), conf.get("log"))
    def send_dict(self, send:dict)->tuple[dict, dict]:
        if 'think' in send:
            think = send.get("think")
            del send['think']
            dz.dset(send,["extra_body", "enable_thinking"], think)
        rsp = self.client.chat.completions.create(**send)
        msg = rsp.choices[0].message
        usage = rsp.usage
        usage =dz.maps(
            total = usage.total_tokens,
            send = usage.prompt_tokens,
            recv = usage.completion_tokens
        )
        role, content, think = dz.og(msg, role=None, content=None, reasoning_content=None)
        rst = dz.maps(role=role,  content=content, think=think, tool_calls=self.out_tool_calls(msg))
        return rst, usage
