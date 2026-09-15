
from .data import Data


@Data.wrap_from
class Relation(Data):
    _data_ks = "date,key,content".split(",")
