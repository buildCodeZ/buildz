{
    envs: {
        env.name: "data3"
    }
    namespace: data3
    default_type: obj
    datas: [
        {
            id: test
            type: obj
            args: [1,2,3]
            maps: {4:5,6:7}
            ref: test1
        }
        {
            id: test1
            type: obj
            args: ['no ref']
        }
    ]
}