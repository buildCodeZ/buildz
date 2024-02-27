
import xf
s=r"""
{
    a:b,
    test: ???
    id: 123
    cid: '123'
    content: '''hehe
    hehehe
    '''
    b:,#test
    a:[1,2,3,]
    v:{
        a:r"xx\n"
        b:"\n"
        c:d
        url:"http://test.com.cn"
    }
}
"""
rst = xf.loads(s)
print(rst)