#
import json

def tokens(maps):
    '''
        模拟计算token数（网上问ai的，暂时没用）
    '''
    s = json.dumps(maps, ensure_ascii=False)
    return 1.2*(len(s)//4)