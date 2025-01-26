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