#coding=utf-8

import hashlib

#计算文件hash值
def fhash(fp, hm="sha256", blk_sz = 10240):
	if type(hm) == str:
		hm = getattr(hashlib, hm)()
	with open(fp, 'rb') as f:
		while True:
			bs = f.read(blk_sz)
			if len(bs)==0:
				break
			hm.update(bs)
	return hm.hexdigest()

pass
