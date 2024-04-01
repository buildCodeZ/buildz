{
    envs: {
        env.test: 123
    }
    namespace: data1
    default_type: default
    datas: [
        {
            id: test
            type: object
            source: test.Test
            single: 1
            construct: {
                args: [
                    [env, env.test]
                    [val, 123]
                ],
                maps: {
                    key:[ref, data2.test]
                }
            },
            sets: [
                [obj, [ref, test]]
                [obj1, [ovar, null, args]]
                [ioc, [ioc, conf]]
                {
                    key: conf
                    val: {
                        type: ioc
                        key: conf
                    }
                }
            ],
            calls: [
                [mcall, null, run, [], {}]
            ]
        }
        {
            id: run
            type: mcall
            source: test
            method: run
            args: []
            maps: {}
        }
        {
            id: test.obj
            val: test.show
        }
        {
            id: calls
            type: calls
            calls: [
                [mcall, test, run,,,]
                [call, test.show]
            ]
        }
    ]
}