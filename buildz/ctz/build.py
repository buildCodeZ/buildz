
from .tools import *
import re
class Builder:
    def __init__(self, pt=None, npt = ".*\.pyc"):
        self.pt = pt
        self.npt = npt
    def has_image(self, s):
        '''
        判断镜像是否存在
        '''
        assert 0, 'not impl'
    def has_container(s, tag=None):
        '''
            判断容器是否存在
        '''
        assert 0, 'not impl'
    def has_images(self, ts):
        for s in ts:
            if not self.has_image(s):
                return False
        return True
    def default_test(self, tag):
        '''
            默认测试运行指令
        '''
        assert 0, 'not impl'
    def read_config(self, fp):
        try:
            s = fread(fp).decode("utf-8")
        except Exception as exp:
            print(f"[WARN] read '{fp}' error: {exp}")
            s = ""
        arr = s.strip().split("\n")
        tag_froms = []
        cmds = {}
        offset = 0
        curr = None
        for s in arr:
            s=s.strip()
            if len(s)<2:
                continue
            if s.lower().find("from")==0:
                arr = s.strip().split(" ")[1:]
                arr = [k.strip() for k in arr if k.strip()!=""]
                tag_from = arr[0]
                tag_froms.append(tag_from)
                continue
            elif s[:3] == "#@@":
                if curr is None:
                    continue
                cmds[curr][-1][0]+="\n"+s[3:]
            elif s[:2]=="#@":
                s = s[2:]
                # if curr is not None:
                #     cmds[curr][-1]+=s
                #     continue
                # curr = None
                i=s.find("=")
                if i<=0:
                    continue
                key = s[:i].strip()
                curr=key
                val = s[i+1:]
                # if val[-1]=="\\":
                #     val = val[:-1]
                #     curr = key
                if key not in cmds:
                    cmds[key] = []
                cmds[key].append([val, offset])
                offset+=1
        if 'test' not in cmds and 'tag' in cmds:
            cmds['test'] = [[self.default_test(cmds['tag'][0][0]), offset]]
        orders = []
        for k, lst in cmds.items():
            for it in lst:
                orders.append(it+[k])
        orders.sort(key = lambda x:x[1])
        return tag_froms, cmds, orders
    def check_read(self, fp):
        if self.pt is not None:
            if len(re.findall(self.pt, fp))>0:
                return True
        if self.npt is not None:
            if len(re.findall(self.npt, fp))>0:
                return False
        return True
    def scan(self, dp, out = {}):
        files = os.listdir(dp)
        #print(f"[DEBUG] scan {dp}, init out: {out}, files: {files}")
        for fp in files:
            fp = os.path.join(dp, fp)
            if not self.check_read(fp):
                #print(f"[DEBUG] check_read False on '{fp}'")
                continue
            if os.path.isfile(fp):
                tfroms, cmds, orders = self.read_config(fp)
                if 'tag' not in cmds:
                    continue
                for tname, _ in cmds['tag']:
                    out[tname] = [fp, tfroms, cmds, orders]
                #out[tname] = [fp, tfroms, test]
            elif os.path.isdir(fp):
                self.scan(fp, out)
        return out
    def builds(self, tag, dirpath = ".", maps=None):
        #print(f"[DEBUG] start builds image '{tag}'")
        if self.has_image(tag):
            print(f"image '{tag}' already builded")
            return None, 0
        maps = maps or self.scan(dirpath)
        assert tag in maps, f"{tag} file not found in {dirpath}"
        fp, tfroms, cmds, orders = maps[tag]
        dp = os.path.dirname(fp)
        for tfrom in tfroms:
            if not self.has_image(tfrom):
                _, ret = self.builds(tfrom, dirpath, maps)
                if ret!=0:
                    return maps, ret
        for s, offset, key in orders:
            if key=='exec':
                ret = os.system(s)
                if ret!=0:
                    print(f"system exec '{s}' error: {ret}")
                    return maps, ret
            elif key=='try':
                ret = os.system(s)
                if ret!=0:
                    print(f"[warn] system try '{s}' error: {ret}")
            elif key=='py.exec':
                exec(s)
            elif key=='py.eval':
                ret = eval(s)
                if type(ret)==int and ret!=0:
                    print(f"python eval '{s}' error: {ret}")
                    return maps, ret
        ret = self.build(fp, tag, dp)
        return maps, ret
    def build(self, fp, tag, dp):
        #print(f"[DEBUG] single build image '{tag}', in fp {fp}, dp: {dp}")
        s = self.build_cmd(fp, tag, dp)
        lines = "="*10
        lines = "\n"+lines+"\n"
        print(lines)
        print(f"@@@ TRY BUILD '{tag}' BY '{s}':")
        print(lines)
        ret = os.system(s)
        print(lines)
        if ret!=0:
            print(f"@@@ error build '{tag}': ret={ret}")
        else:
            print(f"@@@ done build '{tag}'")
        print(lines)
        return ret
    def test(self, tag, dirpath = ".", maps=None):
        maps, ret = self.builds(tag, dirpath, maps)
        if ret!=0:
            return
        maps = maps or self.scan(dirpath)
        fp, tfroms, cmds, orders = maps[tag]
        for stest, _ in cmds['test']:
            print(f"[DEBUG] test with '{stest}'")
            os.system(stest)
    def demo(self):
        order = sys.argv[1]
        tag = sys.argv[2]
        dp = "."
        if len(sys.argv)>3:
            dp =sys.argv[3]
        if order == 'test':
            self.test(tag, dp)
        elif order == 'build':
            self.builds(tag, dp)
        else:
            print(f'unknown command "{order}"')

pass