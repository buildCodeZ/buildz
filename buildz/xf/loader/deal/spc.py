from .. import base


class PrevSpcDeal(base.BaseDeal):
    """
        去掉左空格
    """
    def prev(self, buffer, queue, pos):
        if buffer.size()>0:
            return False
        c = buffer.read()
        if len(c)==0:
            return False
        if len(c.strip())==0:
            buffer.pop_read()
            return True
        return False

pass