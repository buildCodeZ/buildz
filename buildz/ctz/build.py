
from .tools import *
import re
import platform 
class Builder:
    def __init__(self, pt=None, npt = ".*\.pyc"):
        self.pt = pt
        self.npt = npt
        self.args = {}
    def default_args(self):
        args = {}
        sys = platform.system().lower()
        args['TARGETOS'] = sys
        args['TARGETARCH']=platform.machine().lower()
        args['TARGETPLATFORM'] = args['TARGETOS']+"/"+args['TARGETARCH']
        args['TARGETVARIANT'] = ""
        self.args.update(args)
    def init_args(self, s_args):
        s_args = s_args.replace("\\", " ")
        pt = "--build-arg\s+([^\s=]+)=([^\s]+)"
        rst = re.findall(pt, s_args)
        for k,v in rst:
            self.args[k] = v
    def replace_args(self, s, args):
        pt1 = "(\$\{([^\{\}\$\s]+)\})"
        pt2 = "(\$([\w\d_]+))"
        for pt in [pt1, pt2]:
            rst = re.findall(pt, s)
            for rp, k in rst:
                if k not in args:
                    continue
                v = args[k]
                s = s.replace(rp, v)
        return s
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
        args = {}
        args.update(self.args)
        for s in arr:
            s=s.strip()
            if len(s)<2:
                continue
            if s.lower().find("arg")==0:
                tmp = s[3:].strip()
                _i = tmp.find("=")
                if _i<0:
                    continue
                k = tmp[:_i].strip()
                v = tmp[_i+1:].strip()
                args[k] = v
                pass
            if s.lower().find("from")==0:
                arr = s.strip().split(" ")[1:]
                arr = [k.strip() for k in arr if k.strip()!=""]
                lws = [k.lower() for k in arr]
                if 'as' in lws:
                    arr = arr[:lws.index('as')]
                tag_from = arr[-1].split("@")[0]
                tag_from = "/".join(tag_from.split("/")[-2:])
                tar_from = self.replace_args(tag_from, args)
                tag_froms.append(tag_from)
                continue
            elif s[:3] == "#@@":
                if curr is None:
                    continue
                cmds[curr][-1][0]+="\n"+s[3:]
            elif s[:2]=="#@":
                s = s[2:]
                i=s.find("=")
                if i<=0:
                    continue
                key = s[:i].strip()
                curr=key
                val = s[i+1:]
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
    def exec(self, fp, dp=None, orders=None, pfx=""):
        it = self
        if dp is not None:
            fp = os.path.join(dp, fp)
        if orders is None:
            tfroms, cmds, orders = self.read_config(fp)
        for s, offset, key in orders:
            if key==pfx+'exec':
                ret = os.system(s)
                if ret!=0:
                    print(f"system exec '{s}' error: {ret}")
                    return ret
            elif key==pfx+'try':
                ret = os.system(s)
                if ret!=0:
                    print(f"[warn] system try '{s}' error: {ret}")
            elif key==pfx+'py.exec':
                exec(s)
            elif key==pfx+'py.eval':
                print(f"eval: {s}")
                ret = eval(s)
                print(f"[DEBUG] py.eval({s}): {ret}")
                if type(ret)==int and ret!=0:
                    print(f"python eval '{s}' error: {ret}")
                    return ret
        return 0
    def builds(self, tag, dirpath = ".", s_args="", maps=None):
        #print(f"[DEBUG] start builds image '{tag}'")
        if self.has_image(tag):
            print(f"image '{tag}' already builded")
            return None, 0
        maps = maps or self.scan(dirpath)
        #assert tag in maps, f"{tag} file not found in {dirpath}"
        if tag not in maps:
            print(f"[WARN] images '{tag}' not buildfile found")
            return maps, 2
        fp, tfroms, cmds, orders = maps[tag]
        dp = os.path.dirname(fp)
        print(f"[DEBUG] tfroms: {tfroms}")
        for tfrom in tfroms:
            if not self.has_image(tfrom):
                _, ret = self.builds(tfrom, dirpath, s_args, maps)
                if ret!=0:
                    print(f"[WARN] images '{tfrom}' build failed")
                    #return maps, ret
        ret=self.exec(fp, None, orders)
        if ret!=0:
            return maps, ret
        #tags = ",".join([k[0] for k in cmds['tag']])
        ret = self.build(fp, tag, dp, s_args)
        if ret!=0:
            return maps, ret
        ret=self.exec(fp, None, orders, "$")
        return maps, ret
    def build_cmd(self, fp, tag, dp, s_args=""):
        assert 0, 'not impl'
    def build(self, fp, tag, dp, s_args=""):
        #print(f"[DEBUG] single build image '{tag}', in fp {fp}, dp: {dp}")
        s = self.build_cmd(fp, tag, dp, s_args)
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
    def test(self, tag, dirpath = ".", s_args = None, maps=None):
        maps, ret = self.builds(tag, dirpath, s_args, maps)
        if ret!=0:
            print(f"[WARN] image '{tag}' build failed")
            return ret
        maps = maps or self.scan(dirpath)
        fp, tfroms, cmds, orders = maps[tag]
        ret = 0
        for stest, _ in cmds['test']:
            print(f"[DEBUG] test with '{stest}'")
            ret = os.system(stest)
        return ret
    def demo(self):
        args = sys.argv[1:]
        order = args.pop(0)
        tag = args.pop(0)
        dp = "."
        if len(args)>0:
            dp =args.pop(0)
        more_args = " ".join(args)
        self.init_args(more_args)
        if order == 'test':
            ret = self.test(tag, dp, s_args = more_args)
        elif order == 'build':
            _, ret = self.builds(tag, dp, s_args = more_args)
        elif order == 'exec':
            ret = self.exec(tag, dp)
        elif order == '$exec':
            ret = self.exec(tag, dp, None, "$")
        else:
            print(f'unknown command "{order}"')
            ret = 123
        return ret

pass
