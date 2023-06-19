# confz
```
一个类似json的数据交换格式，取名叫做confz，并用python实现了读写代码，另外还根据confz写了个代码配置框架
a json-like file format's read and write code by python, also write a code building framework configure by confz, english description is in "2) english"

update:
新增buildz.xconfz，用模式化的代码重构buildz.confz，让代码更容易维护（相应的速度会更慢些），目前只重构了loads
add sub module buildz.xconfz, which reconstruct buidlz.confz by modularized code, making it easier to update(and run slower), currently only reconstruct method 'loads'
```

## 1) 简介
```
1. confz(buildz.confz)
和json主要区别:
  1，默认所有值都是字符串，而如果没有包含confz的关键字，不需要用引号引起来；
  2，换行符\n和逗号,和分号;都作为分割符; 单引号和双引号具有一样的效果
  3，可以写注释，单行注释用#，多行注释用### 注释 ###
  4, 字符串可以多行，用'''字符串'''或"""字符串"""
  5, 如果要confz不把取值当作字符串，要写在尖括号<>里: <数值, 数据类型>，比如整数10写成<10, int>, 浮点数11.1写成<11.1, float>，布尔类型true写成<true, bool>，None写成<-, null>
写这个东西是为了方便写配置文件和读配置文件，xml感觉有点麻烦，直接用json又要写很多引号，就对json做了简化
confz的关键字如下:
  {}[]()<>:'"#\n,;
一个简单的例子和json作比较:
  json:
  {
    "basedir": "D:\demo",
    "key": "demo",
    "maxdepth": 10
  }
  confz:
  {
    # 基本路径，因为取值包含关键字":", 需要用引号引起来
    basedir: "D:\demo"
    # 搜索关键字
    key: demo
    # 最大文件深度
    maxdepth: <10, int>
  }
主要方法:
  read(s): 把confz格式的字符串s转换成object
  loadfile(s, coding="utf-8"): 从文件s读取confz格式字符串并转换成object，默认编码utf-8
  output(obj): 把数据obj转换成confz格式字符串，这里要注意的是output输出的字符串做了基本的换行
目前只有读和写的代码，之后有空的话可能会写一个confz格式校验代码

2. 控制反转框架(buildz.build, buildz.base)
    根据confz写的控制反转框架（IoC框架）：buildz.Builder或buildz.main
    具体描述在buildz.keys里，可以调用buildz.keys.help()查看，或者运行"python -m buildz ? ch"来查查，另外包里有个例子可以看下：buildz/demo
        测试：在demo文件夹中打开命令行，运行：
            1) python test.py ./demo.confz ./value.confz
            或
            2) python test.py ./run.confz
        1)和2)是等价的，另外如果把buildz当作python来安装，也可以这样运行:
            1) python -m buildz ./demo.confz ./value.confz
            或
            2) python -m buildz ./run.confz

```
## 2) english:
```
1. confz(buildz.confz)
(1) remain char:
    {}[]()<>:'"#\n,;
   to write a string contain remain char, user '' or "" or " x3 or ' x3: 
    "hello:world, 'zero'" 
    'hello:world, "zero"'
    """zero say: "hello, 'world'!" """
(2) from string to obj:
    read(s)
(3) from obj to string:
    output(obj)
(4) from filepath to obj:
    loadfile(filepath, coding="utf-8")
(5) simple read filepath to string:
    fread(filepath)
example:
demo.txt:
[
    # single line note
    {
        filepath: "D:\demo\demo.txt"
        key: test.com
        array: [1, 2, 3]
    }
    {
        test: ":test{}??", 
        val: <10, int>, 
        cost: <10.0, float>, 
        check: <true, bool>, 
        <10, int>: "test"
    }
    #multi-line string
    """test line
        1
        2
        3
    """
    1
    2
    3
    # type not string
    <4, int>
    <5.0, float>
    <true, bool>
]
code:
obj = confz.loadfile("demo.txt")
obj: [{'filepath': 'D:\\demo\\demo.txt', 'key': 'test.com', 'array': ['1', '2', '3']}, {'test': ':test{}??', 'val': 10, 'cost': 10.0, 'check': True, 10: 'test'}, 'test line\n        1\n        2\n        3\n    ', '1', '2', '3', 4, 5.0, True]
s = confz.output(obj)
print(s):
[
    {
        filepath: "D:\demo\demo.txt"
        key: test.com
        array: [1, 2, 3]
    }
    {test: ":test{}??", val: <10, int>, cost: <10.0, float>, check: <true, bool>, <10, int>: test}
    "test line
        1
        2
        3
    "
    1
    2
    3
    <4, int>
    <5.0, float>
    <true, bool>
]
only realize codes of read and write now,  code of format checking may be writing in future, if I have time.
PS: None write as <-, null> (confz: '{data: <-,null>}' == json: '{"data":null}')
2. IoC framework codes(buildz.Builder, buildz.main)
    description is in buildz.keys, run this code to see: "buildz.keys.help('en')" or "python -m buildz ? en"
    here is an example in buildz/demo
    you can open an commond line in demo folder and run like this:
        1) python test.py ./demo.confz ./value.confz
        or:
        2) python test.py ./run.confz
    1) and 2) is equivalent, besides, if you install buildz as python lib, you can also run like this:
        1) python -m buildz ./demo.confz ./value.confz
        or
        2) python -m buildz ./run.confz
```
