#

from ..base import Base
from .. import xf, dz, pyz, log as logz
import subprocess
class Runner(Base):
    """
        子进程调用和杀子进程的封装
        单个子进程，每次调用都会把前面的子进程运行先关闭
    """
    def init(self, commands, log = None):
        log = log or logz.simple()
        self.log = log("subrun")
        self.commands = commands
        self.process = None
        self.exist_psutil = True
        self.reset()
    def reset(self):
        self.kill()
    def kill_chs(self, pid):
        if not self.exist_psutil:
            return
        try:
            import psutil
        except ModuleNotFoundError as exp:
            self.exist_psutil = False
            self.log.warn(f"psutil not installed, children process of subprocess will not being killed")
            self.log.warn(f"if children processes exists and need to be killed, do 'pip install psutil' by yourself and restart")
            self.log.warn(f"没有装psutil，本代码无法删除目标进程的子进程，如果需要本代码删除子进程，需要装psutil然后重启: pip install psutil")
            return
        try:
            parent_process = psutil.Process(pid)
            children = parent_process.children(recursive=True)
            for child in children:
                child.kill()
        except psutil.NoSuchProcess as exp:
            pass
    def kill(self, kill_childs = True):
        if self.process is None:
            return
        if kill_childs:
            self.kill_chs(self.process.pid)
        self.process.kill()
        self.process = None
    def process_exec(self, commands):
        if type(commands)==str:
            commands = commands.split(" ")
        p = subprocess.Popen(commands)
        self.process = p
    def update(self, commands=None):
        commands = commands or self.commands
        self.kill()
        self.process_exec(commands)
    def call(self, *a, **b):
        self.update(*a, **b)
