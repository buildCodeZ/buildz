// [[id, type], key]
[
    {
        nullable: 0,
        out: 1,
        conf: {
            sort:-1,
            data:[
                {key: id, default: null},
                {key: type, default: null }
            ]
        }
    },
    {
        nullable: 0,
        key: key
    },
    {
        nullable: 1,
        key: default
        default: null
    }
]