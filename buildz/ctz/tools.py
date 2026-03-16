
import subprocess, os, sys, re
from os.path import isfile, exists, isdir
from os import system
def cmd(command):
    """
    获取命令执行的输出结果
    """
    try:
        # 使用subprocess.run捕获输出
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return e.stderr
        print(f"命令执行失败: {e.stderr}")
        raise e

pass
def check_tcp(ip, port):
    import socket
    skt=socket.socket()
    skt.settimeout(5.0)
    try:
        skt.connect((ip, port))
        return True
    except:
        return False
    finally:
        skt.close()

pass
def assert_exec(val, cmds):
    if not val:
        return os.system(cmds)

def assert_fc(val, fc, *a, **b):
    if val:
        return
    return fc(*a, **b)

def fread(fp, mode='rb'):
    with open(fp, mode) as f:
        return f.read()

pass