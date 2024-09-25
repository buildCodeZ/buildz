calls: [log, cache, def.deal.type, list, cache.save]
cache: cache/cache.js
cache.save: cache/cache.js
log: log/%Y%m%d_log.txt
def.deal: {
    types: {
        http.get: [request, verify, save]
        get: [request.get, verify, save]
    }
}