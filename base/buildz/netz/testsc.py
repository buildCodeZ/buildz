

def test(n):
    n = yield [n+1], n+2
    n = yield [n*10],n*10+1
    yield [n*3], n*3+1

pass

def wrap_yield(obj):
    first_call=[False]
    def fc(recvs=[]):
        sends,rst=[],None
        if not first_call[0]:
            sends, rst = obj.send(None)
            first_call[0]=True
        for recv in recvs:
            try:
                snds, rst = obj.send(recv)
                sends+=snds
            except StopIteration:
                pass
        return sends, rst
    return fc
pass


def main():
    n=10
    obj = test(n)
    fc = wrap_yield(obj)
    snds, rst = fc()
    print(snds, rst)
    snds, rst = fc([11,110,330])
    print(snds, rst)
    snds, rst = fc([110])
    print(snds, rst)
    snds, rst = fc([330])
    print(snds, rst)


if __name__=="__main__":
    main()
