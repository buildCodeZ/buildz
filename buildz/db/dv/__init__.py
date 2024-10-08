#

def build(dv,*a,**b):
    if dv == 'mysql':
        from .mysqlz import build as _build
    elif dv == 'oracle':
        from .oraclez import build as _build
    elif dv == 'clickhouse':
        from .clickhousez import build as _build
    return _build(*a, **b)

pass
    

