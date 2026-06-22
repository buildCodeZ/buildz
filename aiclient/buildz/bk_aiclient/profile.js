// 本地或远程连接地址
url: "http://127.0.0.1:11434/v1"
// 远程连接需要服务器的api_key，本地的ollama写ollama就可以
api_key: ollama
// 使用的模型
model: "qwen3:0.6b"
// 一次问答最多可以调用ai模型多少次，-1表示不限制次数
max_loop=-1
// 缓存(个数)
cache_size=100
// 缓存的key的最大长度（超过会转换成hash值）
cache_key_size=64
//是否提醒模型注意上下文最大tokens数量（提醒模型尽量不要一次读取太多数据）
//感觉没啥用，小模型完全不管，大模型后面再试
notice_context=false
//是否只提醒一次
notice_only_once=true
// 初始化信息（发给ai模型的）
messages: [
    {
        role: system
        content: "你是一个智能助手。如果用户的问题需要和外界环境交互，就调用相应的工具，不要自己编造数据。"
    }
]
// 日志文件路径
log: "./logs/aiclient_%Y%m%d_%H%M.log"
// 日志显示级别
log_shows: [info,warn, error]

// file技能的配置
file_profile: {
  // 白名单
  whitelist: [
  ]
  // 黑名单
  blacklist: [
    // buildz.aiclient目录
    ('aiclient','.')
    // skills目录
    ('skills', '')
    // 测试，用户目录下的test_buildz
    "~/test_buildz"
    // 测试
    "/home/zzz/test_buildz"
  ]
  // 不在黑名单，又不再白名单下的路径，默认是可以访问还是不能访问
  default_pass: true
}
