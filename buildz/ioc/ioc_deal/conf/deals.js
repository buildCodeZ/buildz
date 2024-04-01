{
    deals: [
        {
            type: val,
            build: buildz.ioc.ioc_deal.val.ValDeal,
            aliases: ['default']
        },
        {
            type: object,
            build: buildz.ioc.ioc_deal.obj.ObjectDeal
        },
        {
            type: env,
            build: buildz.ioc.ioc_deal.env.EnvDeal
        },
        {
            type: ref,
            build: buildz.ioc.ioc_deal.ref.RefDeal
        },
        {
            type: mcall,
            build: buildz.ioc.ioc_deal.mcall.MethodCallDeal
        },
        {
            type: ovar,
            build: buildz.ioc.ioc_deal.ovar.ObjectVarDeal
        },
        {
            type: call,
            build: buildz.ioc.ioc_deal.call.CallDeal
        },
        {
            type: var,
            build: buildz.ioc.ioc_deal.var.VarDeal
        },
        {
            type: calls,
            build: buildz.ioc.ioc_deal.calls.CallsDeal
        },
        {
            type: ioc,
            build: buildz.ioc.ioc_deal.ioc.IOCObjectDeal
        }
    ]
}