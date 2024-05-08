from .. import base
from .. import item
from .. import exp
from ... import file
import json
from . import lr
class PrevStrDeal(lr.LRDeal):
    def prepare(self, mg):
        super().prepare(mg)
        self.label_l2 = mg.like("\\")
        self.label_qt = mg.like('"')
        self.label_et = mg.like("\n")
        self.label_lr = mg.like("\r")
        self.label_nl = mg.like("")
        self.et_in_right = self.right.count(self.label_et)
    def init(self, left = '"', right= '"', single_line = False, note = False, translate = False):
        super().init(left, right, 'str')
        self.single_line = single_line
        self.note = note
        self.translate = translate
    def json_loads(self, s):
        x = s
        cd = None
        if type(x)==bytes:
            x, cd = file.decode_c(x)
        rs = json.loads(x)
        if type(s)==bytes:
            rs = rs.encode(cd)
        return rs
    def do_translate(self, s):
        """
            取巧直接调用json
        """
        qt = self.label_qt
        ql = self.label_l2
        et = self.label_et
        tr = self.label_lr
        nt = self.label_nl
        pt = ql+qt
        arr = s.split(pt)
        arr = [k.replace(qt, pt) for k in arr]
        s = pt.join(arr)
        #s = s.replace(qt, ql+qt)
        s = s.replace(tr, nt)
        arr = s.split(et)
        outs = [self.json_loads(qt+k+qt) for k in arr]
        outs = et.join(outs)
        return outs
    def deal(self, buffer, rst, mg):
        cl = buffer.read(self.ll)
        if cl != self.left:
            return False
        rm = buffer.full().strip()
        buffer.clean2read(self.ll)
        if len(rm)>0 and not self.note:
            if not self.note:
                print("left:", self.left, rm)
                print(f"rst: [{rst}]")
                raise Exception(f"unexcept char before string: {rm}")
            else:
                rst.append(item.Item(rm, type = "", is_val = 0))
        tmp = cl[:0]
        ctmp = tmp[:0]
        do_judge = 1
        mark_et = 0
        mark_l2 = 0
        while True:
            if do_judge and self.right == buffer.rget(self.lr):
                break
            c = buffer.read_cache(1)
            if do_judge and c == self.label_et:
                mark_et += 1
            if len(c)==0:
                if self.single_line and self.note:
                    break
                raise Exception(f"unexcept string end while reading str")
            do_judge = 1
            if c == self.label_l2:
                mark_l2 = 1
                do_judge = 0
                c = buffer.read_cache(1)
                if len(c)==0:
                    raise Exception(f"unexcept string end while reading str")
        data = buffer.full()
        data = data[:-self.lr]
        buffer.clean()
        mark_et -= self.et_in_right
        if self.single_line and mark_et>0:
            print("left:",self.left, "right:", self.right)
            raise Exception(f"contain enter in single line string")
        if self.translate and mark_l2:
            data = self.do_translate(data)
        if self.note:
            return True
        rst.append(item.Item(data, type='str', is_val = 1))
        return True

pass
