#
from .build import * 

class PodmanBuilder(Builder):
    def has_image(self, s):
        if s == 'scratch' or s == 'local/scratch':
            return True
        _s = "localhost/"+s
        rst = cmd('podman images --format "{{.Repository}}:{{.Tag}}"|grep "'+s+'"').strip()
        return rst == s or rst == _s
    def has_container(self, s, tag=None):
        '''
            判断容器是否存在
        '''
        if tag is None:
            cmp = s
            cmpx = cmp
            s = 'podman ps -a --format "table {{.Names}}"|grep "'+s+'"'
        else:
            cmp = f"{s}:{tag}"
            cmpx = f"{s}:localhost/{tag}"
            s = 'podman ps -a --format "table {{.Names}}:{{.Image}}"|grep "'+cmp+'"'
        rst = cmd(s).strip()
        return rst == cmp or rst == cmpx
    def default_test(self, tag):
        return f"podman run --userns=keep-id -it --rm {tag}"
    def build_cmd(self, fp, tag, dp, s_args=""):
        return f"podman build -f {fp} -t {tag} {dp} && podman image prune -f"

if __name__=="__main__":
    exit(PodmanBuilder().demo())

pass
