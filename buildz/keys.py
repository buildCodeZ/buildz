#coding=utf-8
english = """
1. value:
    1) string
        {
            key: {key}
            val: {value}
        }
    2) int, float, bool
        {
            key: {key}
            val: <{value}, {type}>
        }
    3) from source code:
        {
            key: {key}
            import: {package}
            # var, not val
            var: {var}
        }
    4) value or method from object:
        {
            key: {key}
            ref: {ref}
            # var, not val
            var: {var}
        }
    5) list:
        {
            key: {key}
            args: [
                ...
            ]
        }
    6) dict:
        {
            key: {key}
            # notice this is "[", not "{"
            maps: [
                ...
            ]
        }
    7) just is {data}, not do any transfer
        {
            key: {key}
            data: {data}
        }
2. object:
    {
        # optional, if 0, new every time, else just build a single static object
        single: 0|1
        key: {key}
        import: {import}
        call: {class}
        # optional, should not put with args
        val: {val}
        # optional, should not put with val
        args: [
            ({value}, {type})
            ...
        ]
        # optional
        maps: [
            ({key}, {value}, {type})
            ...
        ]
        # optional, should no with val, args, maps
        data: {data}
        # optional
        calls: [
            ({key}, {type}) #type: call(object.method), fc(static function)
        ]
    }
3. function:
    1) object's method
    {
        key: {key}
        ref: {ref} #optional
        call: {call} #optional, object.{call}(...), if not {call}: object(...)
        val: {val} # optional, should not put with args
        args: [...] # optional, should not put with val
        maps: [...] # optional
        data: {data} # optional, should no with val, args, maps
    }
    # if there is not params in object, put an empty args or empty maps: {key:{key}, ref:{ref}, args:[]}
    2) static function
    {
        key: {key}
        import: {import}
        call: {call}
        val: {val} # optional, should not put with args
        args: [...] # optional, should not put with val
        maps: [...] # optional
        data: {data} # optional, should no with val, args, maps
    }
4. functions:
    {
        key: {key}
        calls: [
            ...
        ]
    }

"""
chinese = """
1. 定义值:
    1) 字符串
        {
            key: {key}
            val: {value}
        }
    2) int, float, bool
        {
            key: {key}
            val: <{value}, {type}>
        }
    3) 源代码中的变量（常量）:
        {
            key: {key}
            import: {package}
            # var, 不是val
            var: {var}
        }
    4) 对象的变量:
        {
            key: {key}
            ref: {ref}
            # var, 不是val
            var: {var}
        }
    5) list:
        {
            key: {key}
            args: [
                ...
            ]
        }
    6) dict:
        {
            key: {key}
            # 注意是"[", 不是"{"
            maps: [
                ...
            ]
        }
    7) 纯数据，不做任何转换
        {
            key: {key}
            data: {data}
        }
2. object对象:
    {
        # 可选，是否是单例
        single: 0|1
        key: {key}
        import: {import}
        call: {class}
        # 可选，不和args一起
        val: {val} 
        # 可选，不和val一起
        args: [
            ({value}, {type})
            ...
        ]
        # 可选
        maps: [
            ({key}, {value}, {type})
            ...
        ]
        # 可选, 不和val, args, maps一起
        data: {data}
        # 可选
        calls: [
            ({key}, {type}) #type: call(object.method), fc(static function)
        ]
    }
3. function:
    1) object's method
    {
        key: {key}
        ref: {ref} #可选
        call: {call} #可选, object.{call}(...), if not {call}: object(...)
        val: {val} # 可选, 不和args一起
        args: [...] # 可选, 不和val一起
        maps: [...] # 可选
        data: {data} # 可选, 不和val, args, maps一起
    # 如果是调用对象本身，并且对象没有任何输入参数，要写一个空的args或maps: {key:{key}, ref:{ref}, args:[]}
    2) static function
    {
        key: {key}
        import: {import}
        call: {call}
        val: {val} # 可选, 不和args一起
        args: [...] # 可选, 不和val一起
        maps: [...] # 可选
        data: {data} # 可选, 不和val, args, maps一起
    }
4. functions:
    {
        key: {key}
        calls: [
            ...
        ]
    }

"""

def help(lang = 'cn'):
    global chinese, english
    lang = lang.lower()
    if lang in ['cn', 'ch']:
        print(chinese)
    else:
        print(english)

pass

"""

{key: demo1, val: "hello world!"}
{key: demo2, val: <100.0, float>}
demo/val.py:
   a = 10
   class X:pass
   b = X()
   b.c = a
{key: demo3, import: demo.val, var: a}
{key: demo3, import: demo.val, var: b.c}



"""
