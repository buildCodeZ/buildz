
{
    env_spt: "." // split on env id
    spt: "." // split on id
    default_type: 'test' // default type of data
    deep_first: false // 全局查id的时候是从最上层开始找还是从最下层开始找（每一层都可能有配置文件）
    global_env: true //True=环境变量env都是全局的（全局查找），否则优先每个配置文件里查环境变量，查不到才查全局
    global_deal: true //True=类型处理函数deal都是全局的（全局查找），否则优先每个配置文件里查处理函数，查不到才查全局
}