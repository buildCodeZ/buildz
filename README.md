# buildz
```
1，在json格式基础上加了点东西，让配置文件写起来更简单，模块在buildz.xf下
2，基于xf格式写了个ioc控制反转配置文件读取的程序，模块在buildz.ioc下
3，其他工具模块：
    buildz.fz: 文件夹查找
    buildz.pyz: 简化python __import__调用
    buildz.argx: 按格式读命令行参数
    buildz.demo: 使用参考，运行"python -m buildz"会用这个模块

运行python -m buildz查看帮助

1, a profile file format base on json, make it easy to write profile file, module is in buildz.xf
2, a ioc profile file read function base on xf format, module is in buildz.ioc
3, other tools module:
    buildz.fz: file search
    buildz.pyz: make it easier to use python's __import__ function
    buildz.argx: read command argument in special format
    buildz.demo: example codes to use buildz, run "python -m buildz" will use this module

run python -m buildz to see help
```
