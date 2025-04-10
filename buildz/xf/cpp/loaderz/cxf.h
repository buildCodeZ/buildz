
#ifdef __cplusplus
extern "C" {
#endif

typedef void* (*fptr_create)(int type, void* val, int ival);
typedef void (*fptr_dict_set)(void* dict, void* key, void *val);
typedef void (*fptr_list_add)(void* list, void* val);
typedef void* (*fptr_exp)(const char* s);

void* loads(const char* s, void* callback);
void* loadx(const char* s, void* callback);
void* loads_fcs(const char* s, fptr_create fc_create, fptr_dict_set fc_set, fptr_list_add fc_add, fptr_exp fc_exp);
void* loadx_fcs(const char* s, fptr_create fc_create, fptr_dict_set fc_set, fptr_list_add fc_add, fptr_exp fc_exp);
void* testloads(const char* s);
int tests(const char* s);
#ifdef __cplusplus
}
#endif