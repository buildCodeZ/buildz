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
1. ?????????:
    1) ?????????
        {
            key: {key}
            val: {value}
        }
    2) int, float, bool
        {
            key: {key}
            val: <{value}, {type}>
        }
    3) ?????????????????????????????????:
        {
            key: {key}
            import: {package}
            # var, ??????val
            var: {var}
        }
    4) ???????????????:
        {
            key: {key}
            ref: {ref}
            # var, ??????val
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
            # ?????????"[", ??????"{"
            maps: [
                ...
            ]
        }
    7) ??????????????????????????????
        {
            key: {key}
            data: {data}
        }
2. object??????:
    {
        # ????????????????????????
        single: 0|1
        key: {key}
        import: {import}
        call: {class}
        # ???????????????args??????
        val: {val} 
        # ???????????????val??????
        args: [
            ({value}, {type})
            ...
        ]
        # ??????
        maps: [
            ({key}, {value}, {type})
            ...
        ]
        # ??????, ??????val, args, maps??????
        data: {data}
        # ??????
        calls: [
            ({key}, {type}) #type: call(object.method), fc(static function)
        ]
    }
3. function:
    1) object's method
    {
        key: {key}
        ref: {ref} #??????
        call: {call} #??????, object.{call}(...), if not {call}: object(...)
        val: {val} # ??????, ??????args??????
        args: [...] # ??????, ??????val??????
        maps: [...] # ??????
        data: {data} # ??????, ??????val, args, maps??????
    # ???????????????????????????????????????????????????????????????????????????????????????args???maps: {key:{key}, ref:{ref}, args:[]}
    2) static function
    {
        key: {key}
        import: {import}
        call: {call}
        val: {val} # ??????, ??????args??????
        args: [...] # ??????, ??????val??????
        maps: [...] # ??????
        data: {data} # ??????, ??????val, args, maps??????
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
