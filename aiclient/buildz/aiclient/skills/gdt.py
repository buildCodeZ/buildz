
from buildz import dz
from buildz.aiclient import note
from buildz import fz, log as logz, base, dz
import os
from os.path import join,expanduser,realpath
from os import listdir
from re import findall
ac = note.Note()
path_check = None
log=logz.simple()


class GraphData(base.Base):
    '''
        记忆图调用写成skill
    '''
    def init(self):
        self.mems = []
        pass
    def 
