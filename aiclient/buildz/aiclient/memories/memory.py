
from .data import Data
@Data.wrap_from
class Memory(Data):
    '''
        subject: 主体
        object: 客体
        relation: 关联词
        content: 简单描述
        score: 置信度，浮点数
    '''
    _data_ks = "date,subject,object,relation,content,score".split(",")

pass
