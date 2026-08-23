## 2026/04/01
新建
## 2026/05/13
新增buildz._dz.str.*(buildz.dz下新增val2bs和bs2val)
## 2026/06/02
一些修改
## 2026/08/07
version=0.9.48
解决midserver有数据但读取不了的问题，问题原因是blkskt.recv只会返回一条数据，但blkskt的缓存里可能有更多的数据，增加blkskt.readable()判断缓存是否有完整数据可以读
cert证书验证逻辑增加ca判断，签名path_length判断，域名签名判断（本代码里用common_name当域名，因为域名可以有多个，common_name只有一个，这里只需要一个，不做多个判断）

## 2026/08/12
v 0.9.49
增加对netz.sslz证书验证报错的处理，优化midserver的连接socket遍历处理，避免因为中途增加socket而导致遍历报错，总体而言是增加midserver的容错能力

## 2026/08/24
v 0.9.50
加密传输里增加随机数，防止重发，非加密的就不管了