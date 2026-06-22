
from . import ollama
from . import openai
from . import qianwen
interfaces = {}
interfaces['ollama'] = ollama.OllamaApi
interfaces['openai'] = openai.OpenAiApi
interfaces['qianwen'] = qianwen.QianwenApi
def api_build_conf(conf):
    interface = conf.get("interface", None)
    assert interface in interfaces
    cls = interfaces[interface]
    return cls.from_conf(conf)
def api_build(interface, url, api_key):
    assert interface in interfaces
    cls = interfaces[interface]
    return cls(url, api_key)
