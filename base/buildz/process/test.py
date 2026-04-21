

def test():
    print("test subcall")

pass


if __name__=="__main__":
    import os
    os.system("python3 -m buildz.process.pyrun test.js")
'''

python -m buildz.process.fpscall test.js

python -m buildz.process.fpscall --fps test.js --target=buildz.process.test.test
'''
