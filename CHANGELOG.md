## 2025/06/10
buildz.dz修改和加简单单元测试
## 2025/05/27_1
修改对dict和list的处理工具代码(buildz.dz, buildz.argx)
## 2025/05/27
buildz.xf的loadx输入增加空格间隔符可选
## 2025/05/10
修改buildz.db和buildz.sc的子进程的运行指令，使其适配linux下运行
## 2025/05/09
修改buildz.db和buildz.sc
buildz.db.orm默认不做字段转换
buildz.db.sc运行改成子进程模式，这样sql如果运行太慢，重新跑的时候可以不用等原sql跑完
buildz.sc把部分代码改成独立方法，方便扩展
## 2025/05/08
buildz.base.fcBase
## 2025/04/29
脚本写好，通过"python -m buildz.sc 配置文件"调用，监听文件修改，修改后就重新运行配置文件指定代码(通过subprocess创建进程实现)
## 2025/04/28
文件修改监听功能，测试sql和脚本方便(脚本测试待修改，需要使用多进程)
## 2025/04/22
cpp代码bug修复
## 2025/04/20
加线程池，有些画蛇添足的感觉，因为python本身因为GIL锁是单线程
## 2025/04/17
db.orm修改, xf.cpp.pcxf修改
## 2025/04/13
编写和测试java调用c++版xf.loads（没啥用）
## 2025/04/11
增加c++版xf.load*编译指令：
linux/windows:
python -m buildz.xf.cpp.setup
windows+mingw-x64:
python -m buildz.xf.cpp.setup_mingw32
## 2025/04/10
增加C++版的xf.load*，不过只提供了源码，需要使用者自己在buildz/xf/cpp目录下手动编译，见buildz/xf/cpp/README.txt
## 2025/03/22
加一些声明，netz里的
## 2025/03/20
写了个tcp端口转发代码,buildz.netz.tcp
## 2025/03/19
pytorch+cuda，利用pytorch的勾子实现内存缓存模型，昨天写的有问题，今天重写了一个，类路径是buildz.gpuz.torch.DictCache，ResNet也可以拆了
## 2025/03/18
pytorch+cuda实现简单的内存缓存模型，显存进行计算的代码框架，目前只实现线性模型拆分，后续可能会添加ResNet拆分
代码例子见buildz.gpuz.test.test_middle_conv1
## 2025/03/12
netz加上正向代理代码，demo在buildz.netz.test.test_gw里
## 2025/03/10
iocz添加更方便的调用接口
## 2025/03/07
argz和iocz一点修改，基本算是写好了
## 2025/03/06
修改argz,加iocz/encape处理
## 2025/03/05
修改argz
## 2025/03/04
修改argz（新建argzx）
## 2025/02/28
iocz代码编写中，骨架基本搭好了
## 2025/02/27
iocz代码编写中
## 2025/02/24
iocz代码编写中
## 2025/02/12
添加http和https代理和抓包代码(buildz.netz.mhttp)，目前只能代理和抓包，后续会考虑加上报文截断和修改等的简便接口
添加创建公钥私钥、证书和证书签名的代码(buildz.netz.sslz)
测试代码：
    开启抓包服务器
        python -m buildz.netz.test
    调用测试
        python -m buildz.netz.test.test_cli
稍微修改buildz.logz，加了个简化创建代码
添加buildz.iocz模块，是对buildz.ioc代码的优化，目前只写了一点点，用不了
## 2025/02/03
加一些文件处理代码
## 2025/01/27:
ioc.push_vars等函数可选namespace
wrap.load_conf可选flush
## 2025/01/21:
修改xf的读写，读加上报错字符串位置，写改成递归调用减少时间开销
## 2025/01/17:
加了argz模块和evalz模块
argz模块用于命令行参数匹配
evalz模块用于可配置真假判断
命令行还差一个入参转map的
## 2024/12/22:
增加pathz模块，方便处理路径，修改ioc和db
## 2024/12/18:
增加数据映射xz，数据库db增加类似orm功能以及表和索引结构查询功能（目前只写了mysql,oracle,sqlite3的查询），配置文件读写xf的输出增加对ListMap的支持(dumpx, dumpxf)
## 2024/11/11:
新增buildz.tz.xfind，对json做查询用的，功能类似jsonpath，自己实现的原因是好玩，以及不想为了用jsonpath去学对应的语法
## 2024/10/08:
增强auto配置功能，在auto增加数据库使用的封装，后续考虑出文档。。。如果有时间
## 2024/09/25:
修复bug，增强html的搜索功能，增强auto配置功能
auto里加了个request的demo，里面用的requests库，可以直接配置来进行http调用
## 2024/09/24:
增加模块html:html页面解析
增加模块auto:自动化调用

## 2024/09/09
ioc:
    加修饰器
    加配置refs