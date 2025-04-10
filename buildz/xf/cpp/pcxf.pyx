
#coding=utf-8
#from buildz.xf import code as codez
from buildz.base import Args
# class Args:
#     def size(self):
#         return len(self.args)+len(self.maps)
#     def str(self):
#         return f"<Args args={self.args}, maps={self.maps}>"
#     def __init__(self, args, maps):
#         self.args = args
#         self.maps = maps

# pass


cdef extern from "Python.h":
    object PyBytes_FromStringAndSize(const char* v, ssize_t len)
    object PyBytes_FromString(const char* v)

pass
cdef extern from "pc.h":
    ctypedef object (*fptr_create)(int type, void* dt, int val)
    ctypedef void (*fptr_list_add)(object map, object val)
    ctypedef void (*fptr_dict_set)(object map, object key, object val)
    ctypedef object (*fptr_exp)(const char* msg)
    object ploads_fcs(const char* s, fptr_create fc_create, fptr_dict_set fc_set, fptr_list_add fc_add, fptr_exp fc_error)
    object ploadx_fcs(const char* s, fptr_create fc_create, fptr_dict_set fc_set, fptr_list_add fc_add, fptr_exp fc_error)

# pass
cdef object fCreate(int type, void* dt, int ival)noexcept:
    #print("fCreate:")
    if type == 0:
        return None
    elif type == 1:
        return ival!=0
    # elif type == 101:
    #     return True
    # elif type == 102:
    #     return False
    elif type == 2:
        return int(PyBytes_FromString(<const char*>dt))
    elif type == 3:
        return float(PyBytes_FromString(<const char*>dt))
    elif type == 4:
        return PyBytes_FromString(<const char*>dt).decode("utf-8")
    #elif type == 401:
    #    return codez.ub2s(PyBytes_FromString(<const char*>dt))
    elif type == 5:
        return []
    elif type == 6:
        return {}
    elif type == 7:
        return Args(list(),dict())
    return None
pass
cdef void fListAdd(object lst, object data)noexcept:
    #print("fListAdd:", lst, data)
    lst.append(data)
cdef void fListAddx(object lst, object data)noexcept:
    #print("fListAdd:", lst, data)
    if type(lst)==Args:
        lst = lst.args
    lst.append(data)
cdef void fMapSet(object map, object key, object val)noexcept:
    #print("fMapSet:", map, key, val)
    if type(key)==list:
        key = tuple(key)
    map[key]=val
cdef void fMapSetx(object map, object key, object val)noexcept:
    #print("fMapSet:", map, key, val)
    if type(map)==Args:
        map = map.maps
    if type(key)==list:
        key = tuple(key)
    map[key]=val
cdef object fError(const char* msg)noexcept:
    #print("fError:")
    #print(f"error: msg={msg}")
    s = PyBytes_FromString(msg).decode("utf-8")
    exp_msg = f"error: msg={s}"
    return Exception(exp_msg)

pass
def loads(s,coding="utf-8"):
    if type(s)==str:
        s = s.encode(coding)
    rst = ploads_fcs(s, fCreate,fMapSet,fListAdd,fError)
    if type(rst)==Exception:
        raise rst
    if type(rst)==list and len(rst)==0:
        rst = ''
    if type(rst)==list and len(rst)==1:
        rst = rst[0]
    return rst

pass
def loadx(s,coding="utf-8"):
    """
        和python版loadx区别：
            cpp版没有dict和list，全是Args
    """
    if type(s)==str:
        s = s.encode(coding)
    rst = ploadx_fcs(s, fCreate,fMapSetx,fListAddx,fError)
    if type(rst)==Exception:
        raise rst
    # if type(rst)==list and len(rst)==0:
    #     rst = ''
    if type(rst)==Args and rst.size()==0:
        rst = ''
    # if type(rst)==list and len(rst)==1:
    #     rst = rst[0]
    if type(rst)==Args and rst.size()==1 and len(rst.args)==1:
        rst = rst.args[0]
    return rst

pass
