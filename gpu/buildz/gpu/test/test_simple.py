
from buildz.gpu.torch import recal, dv

import torch
from torch import nn, optim
from buildz import log as logz
log = logz.simple("test_torch.log")
log = log("test.torch.hook")
log.info("new test start")

model = nn.Sequential(nn.Linear(9,6), nn.Linear(6,4), nn.Linear(4,3))
cal_obj = recal.ReCal(102400)
data = torch.randn(11,9)
out = cal_obj(model, data)

ch = cal_obj.caches
for i, dt in ch.items():
    print(f"i[{i}], {dt[0].size()}")

pass
