// [[id, type], key]
// [type, key]
{
    sort: 1
    data: [
        {
            nullable: 0,
            out: 1,
            conf: {
                sort: -1,
                data:[
                    {key: id, default: null},
                    {key: type, default: null}
                ]
            }
        },
        {
            nullable: 1,
            key: key,
            default: conf
        }
    ]
}