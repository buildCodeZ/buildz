#
from .build import * 

class DockerBuilder(Builder):
    def has_image(self, s):
        if s == 'scratch':
            return True
        rst = cmd('docker images --format "{{.Repository}}:{{.Tag}}"|grep "'+s+'"').strip()
        return rst == s
    def has_container(self, s, tag=None):
        '''
            判断容器是否存在
        '''
        if tag is None:
            cmp = s
            s = 'docker ps -a --format "table {{.Names}}"|grep "'+s+'"'
        else:
            cmp = f"{s}:{tag}"
            s = 'docker ps -a --format "table {{.Names}}:{{.Image}}"|grep "'+cmp+'"'
        rst = cmd(s).strip()
        return rst == cmp
    def default_test(self, tag):
        return f"docker run -it --rm {tag}"
    def build_cmd(self, fp, tag, dp, s_args=""):
        return f"docker build -f {fp} -t {tag} {dp} && docker image prune -f"

if __name__=="__main__":
    exit(DockerBuilder().demo())

pass
