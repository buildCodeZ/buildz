

from .datas import Datas
from .relation import Relation

class Relations(Datas):
    def init(self, do_json=True):
        super().init(Relation.from_json, do_json, "relations") 
