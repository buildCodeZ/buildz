{
    
    namespace: data2
    default_type: obj
    datas: [
        {
            id: test
            type: object
            source: test.Test
            construct: {
                args: [
                    [env, env.test]
                    [env, path]
                ]
                maps: {
                    
                }
            }
        }
    ]
}