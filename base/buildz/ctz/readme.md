对dockerfile的扩充

利用备注字段，增加扩充脚本或扩充配置，以#@开头

在不影响原dockerfile文件处理逻辑的情况下，可以使用该工具读取脚本或配置并做相应处理

# 1 用法:

假设是docker(podman用buildz.ctz.pd代替buildz.ctz.dk)

## 1.1 生成镜像：

python -m buildz.ctz.dk build image_name [dirpath]

如果不传dirpath，默认dirpath=当前目录，程序会遍历dirpath目录下的所有文件，把包含"#@tag="的文件当作是dockerfile，找到tag=命令里输的image_name的dockerfile，不存在则build它，在build之前，会扫描该dockerfile包含的FROM，找到其依赖的前置镜像，重复上面的判断和build逻辑

## 1.2 测试镜像：

python -m buildz.ctz.dk test image_name [dirpath]

会执行两个动作：

    1，和上述build一样的逻辑（也就是镜像如果不存在，会先创建）

    2，找到镜像dockerfile里所有的"#@test="语句，作为测试语句，逐条执行，如果没有任何"#@test="语句，则执行默认的测试语句(docker run --rm ...或podman run --rm ...)

建议自己写两个脚本dkbuild.sh和dktest.sh:

dkbuild.sh:
```
python3 -m buildz.ctz.dk build $*
```
dktest.sh:
```
python3 -m buildz.ctz.dk test $*
```

# 2 扩展注释语法：

设置镜像名：
#@tag=???

设置测试方法：
#@test=???

设置build前需要运行的脚本:

#@exec=???
#@try=???
#@py.exec=???
#@py.eval=???

其中exec后面的命令运行失败会报错结束，try后面的命令运行失败会警告然后继续往下
py.exec会把后面的语句当python脚本，运行exec("语句")，py.eval类似，运行eval("语句")，并会判断返回的结果是否是非0整数，是的话会报错

分行写脚本：以"#@@"开头，会被视为上一行的后续

#@test= podman run \
#@@ --name="test" \
#@@ linux:base /bin/bash

# 3 例子:


dk1:

```
from ubuntu:base
RUN ...

#@tag=dk1:1.0
```

dk2:
```
from dk1:1.0
...

#@tag=dk2:1.0
#@test=docker run -it --rm dk2:1.0 /bin/bash
```


执行
python3 -m buildz.ctz.dk build dk2:1.0
build dk2:1.0:
会判断dk2:1.0镜像是否存在，存在则结束
否则：判断dk1:1.0镜像是否存在，存在则继续
    否则: build dk1:1.0:
        ...
