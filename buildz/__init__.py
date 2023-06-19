#from buildz.confz import read, loadfile, output, fread
from buildz.build import Builder, main
from buildz.keys import help
"""
json-like(called 'confz' in here) data format function:
    read: string -> obj
    output: obj -> string
    fread(filepath, coding="utf-8"): filepath -> string 
        #open(filepath, 'rb').read().decode(coding)
    loadfile(filepath, coding="utf-8"): filepath -> obj 
        #equals to read(fread(filepath, coding))

a framework to build code:
    function: main
    Object: Builder
    Description:
        build instance and run from confz format configure file, here is an example in buildz/demo
        从confz格式文件配置中生成对象实例和运行，例子在buildz/demo里

        you can open an commond line in demo folder and run like this:
        测试：在demo文件夹中打开命令行，运行：

            1) python test.py ./demo.confz ./value.confz
            or:
            2) python test.py ./run.confz

        1) and 2) is equivalent
        1)和2)是等价的
"""