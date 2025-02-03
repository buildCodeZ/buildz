{
    id: main
    type: calls
    range: 1
    calls: [
        search
    ]
}
{
    id: search
    type: call
    src: search
    judge: ['=', args[0], search]
    range: 1
    keep: 1
    list: {
        0: {
            des: path
            need: 1
            src: 0
        }
    }
    maps: {
        filepath: {
            srcs: [f, fp, filepath]
        }
        content: {
            srcs: [c, ct, content]
        }
    }
}
