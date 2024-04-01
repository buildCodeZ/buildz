{
text= 
r"""
xf格式的ioc控制反转配置文件读取和生成对象
配置文件格式：
{
    id: 配置文件id，默认null
    //在配置文件配置的环境变量
    envs: {
        id: val
        ...
    }
    // 数据配置项处理逻辑，一般不用管
    deals: {
        {
            type: 要处理的数据类型
            build: 函数import的路径
            args: [] // 列表入参
            maps: {} // 字典入参
        }
    }
    namespace: 命名空间
    locals: [
        本地数据配置项
    ]
    datas: [
        全局数据配置项
    ]
}

预设的数据项格式
1, 数据val:
    {
        // 查找id，可选
        id: id
        type: val
        data: any thing
    }
    简写:
    [[id, val], data] -> [val, data]

2, 对象object:
    {
        id: id
        type: object
        source: 导入路径+调用方法/类
        single: 1 //是否单例，默认是
        construct:{
            args: [
                ...
            ]
            maps: {
                key: {...}
            }
        }
        sets: {
            key: {...}
        }
        calls: [
            ...
        ]
    }
    简写：
    [[id, object, single], source, construct, sets, calls] -> [object, source]

3, 引用
    {
        id: id
        type: ref
        key: 引导数据id
    }
    简写:
    [[id, ref], key] -> [ref, key]

4, 环境变量
    {
        id: id
        type: env
        key: 环境变量key
    }
    简写：
    [[id, env], key] -> [env, key]

5, 对象方法调用：
    {
        id: id
        type: mcall
        source: 对象id
        method: 调用方法
        args: [...]
        maps: {key:...}
    }->
    [[id, mcall], source, method, args, maps]->[mcall, source, method]
6, 函数调用:
    {
        id:id
        type:call
        method: import路径+"."+方法名
        args: [...]
        maps: {key:...}
    }->
    [[id, call], method, args, maps]->[call, method]

7，对象变量
    {
        id:id
        type: ovar
        source: string
        key: string
    }->
    [[id, ovar], source, key] -> [ovar, source, key]

8, 代码变量
    {
        id:id
        type: var
        key: string
    }->
    [[id, ovar], source, key] -> [ovar, source, key]


9，ioc字段
    {
        id:id
        type: ioc
        //default conf
        key: string = conf, confs, sid 
    }->
    [[id, ioc], key] -> [ioc]

10, list
    {
        id: id
        type: list
        data: [...]
    }
11，map
    {
        id:id
        type:map
        data: {
            k: ...
        }
    }
12, join:
    //文件路径合并
    {
        id:id
        type: join
        data: [...]
    }
13, 函数调用:
    {
        id:id
        type:calls
        calls: [...]
    }->
    [[id, calls], calls]->[calls, method]
    

运行：
    python -m buildz ioc 文件夹路径 数据id
"""

}