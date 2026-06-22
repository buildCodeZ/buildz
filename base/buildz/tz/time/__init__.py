from .timez import Clock,clock,timecost,showcost
import time
class Timer:
    def __init__(self):
        self.curr = None
    def start(self):
        self.curr = time.time()
    def __call__(self, reset=False):
        curr = time.time()
        if self.curr is None:
            self.curr = curr
        sec = curr-self.curr
        if reset:
            self.curr = curr
        return sec

pass
