from buildz.base import Base
import re
from . import mapz
class Check(Base):
    '''
        whitelist: [tag1, tag2, ...]
        blacklist: [tag1, tag2, ...]
        default_pass: true/false
    '''
    @staticmethod
    def fc_contain(tag, list):
        return tag in list
    @staticmethod
    def fc_match_any(tag, list):
        for pt in list:
            if len(re.findall(pt, tag))>0:
                return True
        return False
    def str(self):
        return f"Check<self.whitelist: {self.whitelist}, self.blacklist: {self.blacklist}, self.default_pass: {self.default_pass}>"
    @staticmethod
    def build_conf(conf, default_fn = "contain"):
        whitelist, blacklist, default_pass, passes, rejects,default = mapz.g(conf, whitelist=None, blacklist=None, default_pass=False, passes=[], rejects = [], default=False)
        default_pass = default_pass or default
        whitelist = whitelist or passes
        blacklist = blacklist or rejects
        fn = mapz.g(conf, fc=default_fn)
        fc = Check.fc_contain
        if fn == 'contain':
            fc = Check.fc_contain
        elif fn in {'match', 'match_any'}:
            fc = Check.fc_match_any
        elif type(fn)==str:
            assert 0, f"not impl fc type: {fn}, 'contain', 'match' only"
        else:
            fc = fn
        return Check(whitelist, blacklist, default_pass, fc)
    def init(self, whitelist=[], blacklist=[], default_pass=False, fc = None):
        fc = fc or Check.fc_contain
        self.whitelist = set(whitelist)
        self.blacklist = set(blacklist)
        self.default_pass = default_pass
        self.fc = fc
    def add_pass(self, tag):
        self.whitelist.add(tag)
        if tag in self.blacklist:
            self.blacklist.remove(tag)
    def remove_pass(self, tag):
        self.whitelist.remove(tag)
    def add_reject(self, tag):
        self.blacklist.add(tag)
        if tag in self.whitelist:
            self.whitelist.remove(tag)
    def remove_reject(self, tag):
        self.blacklist.remove(tag)
    def set_default(self, val):
        self.default_pass = val
    def call(self, tag):
        rst = self._call(tag)
        #print(f"check '{tag}' result: {rst}, by whitelist: {self.whitelist}, blacklist: {self.blacklist}, default: {self.default_pass}")
        return rst
    def _call(self, tag):
        #print(f"check by fc: {self.fc}")
        if self.fc(tag, self.whitelist):
            #print(f"pass in whitelist")
            return True
        if self.fc(tag, self.blacklist):
            #print(f"not pass in blacklist")
            return False
        #print(f"by default: {self.default_pass}")
        return self.default_pass
        if tag in self.whitelist:
            return True
        if tag in self.blacklist:
            return False
        return self.default_pass

