
from buildz.ctz.tools import cmd

def cpu_temp():
    s=cmd('cat /sys/class/thermal/thermal_zone0/temp')
    v = int(s)*0.001
    return v

def gpu_temp():
    s=cmd("nvidia-smi -q -d TEMPERATURE").strip()
    arr = s.split("\n")
    arr = [k for k in arr if k.lower().find("temp")>=0 and k.lower().find("current")>=0]
    assert len(arr)>0
    rst = arr[0].split(":")[-1].strip()
    rst = rst.split(" ")[0]
    return int(rst)

def disk_temp():
    s = cmd("cat /sys/class/hwmon/hwmon*/name")
    arr = s.strip().split("\n")
    find=-1
    for i in range(len(arr)):
        k = arr[i].strip()
        if k.lower().find("nvme")==0:
            find=i
            break
    assert find>=0
    s = cmd(f"cat /sys/class/hwmon/hwmon{find}/temp1_input").strip()
    v = int(s)*0.001
    return v

def test():
    print(f"CPU: {cpu_temp()} C")
    print(f"GPU: {gpu_temp()} C")
    print(f"Disk: {disk_temp()} C")

pass

if __name__=="__main__":
    test()

pass

