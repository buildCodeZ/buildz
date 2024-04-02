{
    deals: [
        {
            type: val,
            note: 数据, //note是注释，非必须
            build: buildz.ioc.ioc_deal.val.ValDeal,
            aliases: ['default']
        },
        {
            type: object,
            note: 对象,
            build: buildz.ioc.ioc_deal.obj.ObjectDeal
        },
        {
            type: env,
            note: 环境变量,
            build: buildz.ioc.ioc_deal.env.EnvDeal
        },
        {
            type: ref,
            note: 引用,
            build: buildz.ioc.ioc_deal.ref.RefDeal
        },
        {
            type: mcall,
            note: 对象方法调用,
            build: buildz.ioc.ioc_deal.mcall.MethodCallDeal
        },
        {
            type: ovar,
            note: 对象变量,
            build: buildz.ioc.ioc_deal.ovar.ObjectVarDeal
        },
        {
            type: call,
            note: 函数调用,
            build: buildz.ioc.ioc_deal.call.CallDeal
        },
        {
            type: var,
            note: 代码变量,
            build: buildz.ioc.ioc_deal.var.VarDeal
        },
        {
            type: calls,
            note: 调用序列,
            build: buildz.ioc.ioc_deal.calls.CallsDeal
        },
        {
            type: ioc,
            note: 控制反转内部数据,
            build: buildz.ioc.ioc_deal.ioc.IOCObjectDeal
        },
        {
            type: list,
            note: 列表,
            build: buildz.ioc.ioc_deal.list.ListDeal
        },
        {
            type: map,
            note: 字典,
            build: buildz.ioc.ioc_deal.map.MapDeal
        },
        {
            type: join,
            note: 文件路径拼接,
            build: buildz.ioc.ioc_deal.join.JoinDeal
        }
    ]
}