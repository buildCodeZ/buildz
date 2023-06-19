"""
import sys

sys.path.append(r"")

"""
try:
    from buildz import build
except:
    import sys
    import os
    sys.path.append(os.path.abspath("./../.."))
    from buildz import build

build.test()