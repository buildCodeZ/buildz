
from .base import *
class Data(Base):
    '''
        封装的数据对象，包括方法：
            从json对象读取和输出成json对象（其实就是dict和list）
            从xml对象读取和输出成xml对象（自己写的xml对象）
        特殊处理：
            如果_data_ks字段列表包括date字段，会进行特殊处理：
                在创建的时候会自动进行时间戳（秒值）转字符串，如果创建的时候输入参数不包括date字段，会用当前时间的时间戳作为时间戳，转字符串，转换后的字符串时间格式为对象的date_format格式
    '''
    _data_ks = []
    _match_ks = None
    date_format="%Y-%m-%d %H:%M:%S"
    def str(self):
        return self.out_xml()
    def sec2date(self, sec=None):
        sec = sec or time.time()
        return time.strftime(self.format, time.localtime(sec))
    def init(self, *args, **kwargs):
        for i in range(min(len(args), len(self._data_ks))):
            k = self._data_ks[i]
            v = args[i]
            setattr(self, k, v)
        for k in self._data_ks:
            if k in kwargs:
                setattr(self, k, kwargs[k])
        if 'date' in _data_ks:
            date = None
            if hasattr(self, 'date'):
                date = self.date
            if date is None or type(date)!=str:
                self.date = self.sec2date(date)
    def out(self, abs=None):
        if abs is None:
            abs = set()
        elif type(abs)==str:
            abs = [abs]
        abs = set(abs)
        rst = {}
        for k in self._data_ks:
            if k in abs:
                continue
            rst[k] = getattr(self, k)
        return rst
    def out_xml(self, abs=None):
        rst = self.out(abs)
        s = xml.xr(**rst)
        return s
    def out_json(self, abs=None):
        rst = self.out(abs)
        s = dz.jnn(**rst)
        return s
    def match(self, obj):
        ks = self._match_ks or self._data_ks
        for k in ks:
            if getattr(self, k)!=getattr(obj, k):
                return False
        return True
    @staticmethod
    def from_json(obj, cls, ks=None):
        ks = ks or cls._data_ks
        rst = dz.lgets(obj, ks)
        return cls(*rst)
    @staticmethod
    def from_xml(obj, cls, ks=None):
        ks = ks or cls._data_ks
        rst = {}
        for key in ks:
            dts = obj.tags(key)
            if len(dts)>0:
                rst[key] = dts[0].text
            else:
                rst[key] = None
        return cls(**rst)
    @staticmethod
    def from_obj(obj, cls):
        if isinstance(obj, xml.HtmlTag):
            return cls.from_xml(obj)
        else:
            return cls.from_json(obj)
    @staticmethod
    def wrap_from(cls):
        def from_json(obj):
            return Data.from_json(obj, cls)
        def from_xml(obj):
            return Data.from_xml(obj, cls)
        def from_obj(obj):
            return Data.from_obj(obj, cls)
        cls.from_json = staticmethod(from_json)
        cls.from_xml= staticmethod(from_xml)
        cls.from_obj = staticmethod(from_obj)
        return cls



