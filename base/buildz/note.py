

from . import dz,fz,xf, args as argx, log as logz, pyz
import os
log = logz.simple()
s_conf="""
(path, outfile, excepts)
{
   o:ofp
   ofp:outfile
   e:excepts
   exp:excepts
   exps:exp
   except:exp
}
"""
fetch = argx.Fetch(*xf.loads(s_conf))

def match(fps=[]):
    if fps is None:
        fps = []
    if type(fps)==str:
        fps = [fps]
    def fc(fp):
        for _fp in fps:
            if fp.find(_fp)>=0:
                return True
        return False
    return fc
def single_scan(path=".", excepts = [], outfile="structx.txt"):
    fps = fz.search(path, depth=1, pt_fp=".*\.py")
    print(f"fps: {fps}")
    fc = match(excepts)
    fps = [k for k in fps if not fc(k)]
    rst = []
    for fp in fps:
        fn = os.path.basename(fp)
        fn_bk = fn
        fn = fn[:-3]
        dp = os.path.dirname(fp)
        dp = dp.replace("\\","/")
        pkgs = dp.split("/")
        pkgs = [k.strip() for k in pkgs if k.strip()!="."]
        pkgs+=[fn]
        pkgs = ".".join(pkgs)
        try:
            obj = pyz.load(pkgs)
        except Exception as exp:
            print(f"except in load '{fp}||{pkgs}': {exp}")
            print(f"exception detail: {pyz.s_exp()}")
            continue
        doc = obj.__doc__
        if doc is None or type(doc)!=str:
            continue
        doc = doc.strip()
        doc = doc.replace("\n", "\n    ").strip()
        doc = "    "+doc
        rst.append([fn_bk, doc])
    rst = [f"{fn}:\n{doc}" for fn, doc in rst]
    rs = "\n\n".join(rst)
    fz.write(rs.encode("utf-8"), outfile)
    print(f"done and save in {outfile}")



if __name__=="__main__":
    conf = fetch()
    path, excepts, outfile = dz.g(conf, path=".", excepts=None, outfile="./structx.txt")
    single_scan(path, excepts, outfile)

pass
    
