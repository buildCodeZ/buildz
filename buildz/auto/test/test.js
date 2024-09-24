calls: [log, cache, def.deal.type, list, cache.save]
cache: tmp.js
cache.save: tmp.js
log: log.txt
def.deal: {
    types: {
        http.get: [request, verify, save]
    }
}
datas: [
    {
        url: test
        type: http.get
        data: {
            url: "#{test.url}"
        }
        save: {
            test.url: data.url
        }
        result: {
            code: 0.99
        }
        verify: [
            [code, [">", 1]]
        ]
    }
]