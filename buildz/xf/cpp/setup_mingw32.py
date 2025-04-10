#
import sys
if len(sys.argv)==1:
    sys.argv.append("build_ext")
    sys.argv.append("--inplace")
if sys.platform =='win32':
    sys.argv.append("--compiler=mingw32")
import setup