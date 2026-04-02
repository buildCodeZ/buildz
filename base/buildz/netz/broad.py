import socket
class Broad:
    '''
        局域网广播
    '''
    def __init__(self, port: int=5005):
        self.port = port
        # 创建UDP套接字
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 启用广播模式
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.skt = sock
        self.bind = False
    def recv(self, size=1024*1024):
        if not self.bind:
            self.skt.bind(('', self.port))
            self.bind=True
        data, addr = self.skt.recvfrom(size)
        return data, addr
    def send(self, message: bytes, port=None):
        broadcast_addr = '<broadcast>'
        port = port or self.port
        self.skt.sendto(message, (broadcast_addr, port))
    def close(self):
        self.skt.close()

pass
def test():
    import sys, time
    sec=2.0
    od = sys.argv[1].strip().lower()[:1]
    if len(sys.argv)>2:
        sec = float(sys.argv[2])
    broad=Broad()
    try:
        if od == 's':
            while True:
                broad.send(b"test from broadcast")
                print(f"send success")
                time.sleep(sec)
        elif od == 'r':
            while True:
                msg, addr = broad.recv()
                print(f"recive from {addr}: {msg.decode('utf-8')}")
        else:
            assert 0
    finally:
        broad.close()
if __name__=="__main__":
    test()
