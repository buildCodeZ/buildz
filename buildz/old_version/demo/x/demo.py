#coding=utf-8
class Demo:
    def __init__(self, a, b):
        self.a = a
        self.b = b
    def show(self, data):
        print("START SHOW")
        print("self:", self.a, self.b)
        print("input:", data)
        print("FINISH SHOW")
    def __call__(self, data):
        print("CALL __call__ that do nothing")
    def __str__(self):
        return "<Object Demo a=("+str(self.a)+"), b=("+str(self.b)+")>"
    def __repr__(self):
        return str(self)

pass

demo_value = "hello world!"
