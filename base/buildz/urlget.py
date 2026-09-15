#

import requests as rq

import sys
def test():
    args = sys.argv[1:]
    url = args.pop(0)
    if url.find("://")<0:
        url = "http://"+url
    ofp = url.split("?")[0].split("/")[-1].strip()
    if ofp=="":
        ofp = "index.html"
    if len(args)>0:
        ofp = args.pop(0)
    rp = rq.get(url)
    if rp.status_code!=200:
        print(f"get url error: {rp.status_code}")
        exit(0)
    with open(ofp, 'wb') as f:
        f.write(rp.content)
    print(f"save to '{ofp}'")

if __name__=="__main__":
    test()
