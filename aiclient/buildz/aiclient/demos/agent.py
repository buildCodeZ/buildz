

from buildz.aiclient import agent as agentz
from buildz import xf,dz,fz,args ars argx, log as logz
s_conf = '''
messages:[
  {
      role: system
      content: """你是一个擅长构造长篇小说的智能助手。你返回的内容需要符合基本的markdown格式，每一个问题的回答为一个一级标题，问题的主要内容如果要分成小点，用二级标题区分"""
  }
]
client: {
  interface: ollama
  url: "http://192.168.137.2:11434/"
  url: "http://172.17.0.1:10034/"
  send: {
    //model: 'qwen3:14b',
    //model: 'qwen3:0.6b'                                  
    //model: 'local_fdz_qwen36_unc:latest'
    model: 'local_jl_qwen3.8-27B-UD-Q3_K_XL:latest'
    model: 'local_jl_qwen3.8-27B-UD-Q3_K_XL_20490:latest'
    embed_model:"qwen3-embedding:0.6b"
  }
}
log = "./logs/aist_local_%Y%m%d_%H%M.log"
history: history_local.xml
'''
conf = xf.loads(
