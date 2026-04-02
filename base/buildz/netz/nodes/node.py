'''
'''
from ...base import *
class Node(Base):
    def init(self):
        self.running=1
        pass
    def call(self):
        while self.running:
            self.deal()

pass