
import sys
from . import fhs
args = sys.argv[1:]
fp = args.pop(0)
hash_type = "sha256"
if len(args)>0:
    hash_type = args.pop(0)
blk_sz = 1024
if len(args)>0:
    blk_sz = int(args.pop(0))
rst = fhs.fhash(fp, hash_type, blk_sz)
print(f"hash value of '{fp}' by '{hash_type}':\n{rst}")
