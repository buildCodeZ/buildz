calls: [log, cache, def.deal.type, list, cache.save]
cache: cache/cache.js
cache.save: cache/cache.js
log: log/%Y%m%d_log.txt
log.shows: [info, warn, debug, error]
def.deal: {
    types: {
        http.get: [defs, request, verify, save]
        get: [defs, request.get, verify, save]
    }
}