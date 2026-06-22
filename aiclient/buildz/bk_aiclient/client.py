from openai import OpenAI
# from . import tools
import json, os
from buildz import args as argx, xf, fz, log as logz, dz
from .tool import ToolsManager
conf_args = r"""
[url, api_key, model]
{
    p:profile
    profile:profile_path
    m:model
    md: model
    a:api
    api:api_key
    u:url
    h:help
    t:tools_folder
    l:log
    s:show
    show:shows
    shows:log_shows
    t:max_tokens
    ot:ollama_num_ctx
    xt:max_completion_tokens
}
[h, help]
"""
dp = os.path.dirname(__file__)
default_fp=os.path.join(dp, "profile.js")
class Client:
    def build(self, conf, log=None):
        url = conf.get("url")
        api_key = conf.get("api_key")
        self.model = conf.get("model")
        client = OpenAI(
            base_url=url,
            api_key=api_key
        )
        messages = conf.get("messages", [])
        self.max_loop=conf.get("max_loop", -1)
        self.client = client
        self.conf = conf
        tl_dp = conf.get("skills_folder", None)
        if log is None:
            log_fp = conf.get("log")
            log_shows = conf.get("log_shows")
            log = logz.simple(log_fp, shows=log_shows)
        self.log = log("client")
        self.tools = ToolsManager(tl_dp, self.conf, self.log)
        self.tools.scan()
        self.max_tokens = int(conf.get("max_tokens", 0))
        self.max_completion_tokens = int(conf.get("max_completion_tokens", 0))
        self.ollama_num_ctx = int(conf.get("ollama_num_ctx", 0))
        self.notices=None
        notice_only_once = conf.get("notice_only_once", True)
        if notice_only_once:
            self.notice_times = 1
        else:
            self.notice_times = -1
        if self.max_tokens>0 and conf.get("notice_context", True):
            self.notices = {
                "role": "system",
                "content": f"注意运行模型context最大只有{self.max_tokens}tokens"
            }
        self.src_messages = messages
        self.messages = list(self.src_messages)
    def deal(self, s):
        self.messages.append({"role": "user", "content": s})
        cnt = self.max_loop
        while cnt!=0:
            cnt=cnt-1
            # 1. 调用模型
            p_tools = self.tools.out()
            # self.log.debug(f"chat with {self.model}, msg: {self.messages}, tools: {p_tools}")
            if self.notices and self.notice_times!=0:
                self.messages.append(self.notices)
                self.notice_times-=1
            send = dz.maps(
                model=self.model, # 确保远程服务器上有这个模型
                messages=self.messages,
                tools=p_tools,
                tool_choice="auto" # 让模型自动决定是否需要调用工具
            )
            if self.max_tokens >0:
                send['max_tokens']=self.max_tokens
            if self.max_completion_tokens >0:
                send['max_completion_tokens']=self.max_completion_tokens
            if self.ollama_num_ctx >0:
                send['extra_body']={
                    'num_ctx':self.ollama_num_ctx
                }
            show_sends = dict(send)
            del show_sends['tools']
            del show_sends['messages']
            self.log.debug(f"chat params: {show_sends}")
            self.log.debug(f"   send messages:")
            for msg in send.get("messages"):
                self.log.debug(f"       msg: {msg}")
            self.log.debug(f"   send tools:")
            for ptool in send.get("tools"):
                self.log.debug(f"       tool: {ptool}")
            self.log.debug("done build sended ")
            self.log("系统").info(f"开始调用ai模型接口")
            response = self.client.chat.completions.create(**send)
            choice = response.choices[0]
            self.log.debug(f"response: {len(response.choices)}")
            #usage=CompletionUsage(completion_tokens=352, prompt_tokens=411, total_tokens=763, completion_tokens_details=None, prompt_tokens_details=None)
            usage = response.usage
            self.log("系统").info(f"本次调用上送数据: {usage.prompt_tokens} tokens, 返回数据:{usage.completion_tokens} tokens, 总数据: {usage.total_tokens} tokens")
            message = choice.message
            reasoning = message.reasoning
            message.reasoning = None
            self.messages.append(message)
            # 2. 检查是否有工具调用
            if message.tool_calls:
                # 模型决定调用工具
                # self.messages.append(message) # 将模型的请求（包含 tool_calls）加入历史
                # 遍历所有被调用的工具 (模型可能一次调用多个)
                for tool_call in message.tool_calls:
                    func_name = tool_call.function.name
                    # 参数字符串转字典
                    func_args = json.loads(tool_call.function.arguments)
                    # 执行本地函数
                    self.log("系统").info(f"执行指令: {func_name}{func_args}")
                    result = self.tools.call(func_name, func_args)
                    # 将执行结果反馈给模型
                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result
                    })
                # 循环继续，将结果发给模型，让它生成最终回答
                self.log("系统").info("工具执行完毕，正在调用模型生成下一次指令")
            else:
                # 没有工具调用，直接输出最终回答
                return message.content
        return f"超过最大调用次数限制({self.max_loop})，未得出答案"
    def main(self):
        while True:
            print("")
            print(f"+-*/"*10)
            print("")
            # self.log("客户端").info(f"等待用户输入指令中")
            user_query = input("请输入指令(exit或quit退出,reset重置对话):").strip()
            if not user_query:
                continue
            if user_query.lower() in ['exit', 'quit']:
                break
            if user_query.lower() == 'reset':
                self.messages = list(self.src_messages)
                if self.notice_times==0:
                    self.notice_times = 1
                self.log("系统").info("对话已经重置")
                continue
            if user_query[:3]=='fp:':
                user_query = fz.read(user_query[3:].strip()).decode("utf-8")
            out = self.deal(user_query)
            self.log("客户端").info(f"回复: {out}")

def test(argv=None):
    args = xf.loads(conf_args)
    fetch = argx.Fetch(*args)
    #self.log.info(f"fetch: {fetch.des()}")
    maps = fetch(argv)
    fp = maps.get("profile_path", default_fp)
    conf = xf.loadf(fp)
    conf.update(maps)
    log_fp = conf.get("log")
    log_shows = conf.get("log_shows")
    log = logz.simple(log_fp, shows=log_shows)
    if conf.get("help", False):
        self.log.debug(f"args: {fetch.des()}")
        exit(0)
    log.debug(f"conf: {conf}")
    cli = Client()
    cli.build(conf, log)
    cli.main()

if __name__=="__main__":
    test()


'''
python -m buildz.aiclient -u http://172.17.0.1:11434/v1

python3 -m buildz.aiclient -u http://172.17.0.1:11434/v1 -m qwen3:8b -s info -s warn -s debug -s error
'''
