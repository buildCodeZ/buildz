
from buildz.base import Base
from buildz import xf, fz, dz
from ..api import Api
import json
class OpenAiApi(Api):
    @staticmethod
    def from_conf(conf):
        return OpenAiApi(conf.get("url"), conf.get("api_key"), conf.get("log"))
    def init(self, url, api_key, log=None):
        super().init(log)
        import openai 
        self.url = url
        self.client = openai.OpenAI(base_url = url, api_key = api_key)
    def out_tool_call(self, tool_call):
        fc = tool_call.function
        rst = dz.mapsnn(id=tool_call.id, function=dz.mapsnn(name=fc.name, arguments=json.loads(fc.arguments)))
        return rst
    def out_tool_calls(self, msg):
        tool_calls=msg.tool_calls
        if tool_calls:
            tool_calls = [self.out_tool_call(it) for it in tool_calls]
        return tool_calls
    def send_dict(self, send:dict)->tuple[dict, dict]:
        if 'think' in send:
            think = send.get("think")
            del send['think']
            if think:
                if think==True:
                    think = 'high'
                send['reasoning_effort'] = think
        print(f"[TEST] chat: {send}")
        rsp = self.client.chat.completions.create(**send)
        msg = rsp.choices[0].message
        usage = rsp.usage
        usage =dz.maps(
            total = usage.total_tokens,
            send = usage.prompt_tokens,
            recv = usage.completion_tokens
        )
        role, content, think = dz.og(msg, role=None, content=None, reasoning=None)
        rst = dz.maps(role=role,  content=content, think=think, tool_calls=self.out_tool_calls(msg))
        return rst, usage
    def embed(self, msg:str, model:str)->list[float]:
        resp = self.client.embeddings.create(input=msg, model=model)
        print(f"[TESTZ] resp: {len(resp.data)}")
        return resp.data[0].embedding
