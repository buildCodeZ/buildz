from buildz import xf, fz, dz
import time, os
fs = fz.search("/boot")
btm = time.time()-3600*5
def fetch(fp):
	x = os.stat(fp)
	atm = time.strftime("%Y%m%d %H:%M:%S", time.localtime(x.st_atime))
	mtm = time.strftime("%Y%m%d %H:%M:%S", time.localtime(x.st_mtime))
	ctm = time.strftime("%Y%m%d %H:%M:%S", time.localtime(x.st_ctime))
	return fp, ctm, atm, mtm
def check(fp):
	x = os.stat(fp)
	return x.st_atime>btm or x.st_mtime>btm or x.st_ctime>btm
print(f"fs: {len(fs)}")
arr = [fetch(fp) for fp in fs if check(fp)]
print(xf.dumps(arr, format=1))
