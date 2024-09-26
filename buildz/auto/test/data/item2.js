note: test2
url: "https://$host/"
defs: {
    $host:"#{host}"
}
type: get
headers: {
    User-Agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
}
data: {
}
verify: [
    "status_code, 200"
    "result_headers.Content-Type, 'text/html; charset=utf-8'"
]
save: {
    test2.headers.content_type: result_headers.Content-Type
}