#coding=utf-8

class Base:
    def str(self):
        return str(self.__class__)
    def __str__(self):
        return self.str()
    def __repr__(self):
        return self.__str__()
    def __init__(self, *args, **maps):
        self.init(*args, **maps)
    def __call__(self, *args, **maps):
        return self.call(*args, **maps)
    def init(self, *args, **maps):
        pass
    def call(self, *args, **maps):
        return self.deal(*args, **maps)
    def deal(self, *args, **maps):
        return None

pass