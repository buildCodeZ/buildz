
from buildz.ctz.tools import cmd

def cpu_temp():
    s=cmd('cat /sys/class/thermal/thermal_zone0/temp')
    v = int(s)*0.001
    return v

def gpu_temp():
    s=cmd("nvidia-smi -q -d TEMPERATURE").strip()
    arr = s.split("\n")
    arr = [k for k in arr if k.lower().find("temp")>=0 and k.lower().find("current")>=0]
    if len(arr)==0:
        return -1
    assert len(arr)>0
    rst = arr[0].split(":")[-1].strip()
    rst = rst.split(" ")[0]
    return int(rst)
def hdd_temp():
    s = cmd("cat /sys/class/hwmon/hwmon*/name")
    arr = s.strip().split("\n")
    find=-1
    for i in range(len(arr)):
        k = arr[i].strip()
        if k.lower().find("drivetemp")==0:
            find=i
            break
    if find<0:
        print(f"you could try 'sudo modprobe drivetemp' to enable drivetemp to see hdd temperature")
        return -1
    assert find>=0
    s = cmd(f"cat /sys/class/hwmon/hwmon{find}/temp1_input").strip()
    v = int(s)*0.001
    return v
def disk_temp():
    s = cmd("cat /sys/class/hwmon/hwmon*/name")
    arr = s.strip().split("\n")
    find=-1
    for i in range(len(arr)):
        k = arr[i].strip()
        if k.lower().find("nvme")==0:
            find=i
            break
    if find<0:
        return -1
    assert find>=0
    s = cmd(f"cat /sys/class/hwmon/hwmon{find}/temp1_input").strip()
    v = int(s)*0.001
    return v
def cpu_rate():
    try:
        s = cmd("vmstat 1 2").strip().split("\n")[-1].replace("\t", " ").strip()
        arr = s.split(" ")
        arr = [k.strip() for k in arr if k.strip()!=""]
        us = float(arr[-5])
        sy = float(arr[-4])
        fr = float(arr[-3])
        return us+sy
    except Exception as exp:
        return -1
def test():
    print(f"CPU: {cpu_temp()} C")
    print(f"CPU%: {cpu_rate()} %")
    print(f"GPU: {gpu_temp()} C")
    print(f"Disk: {disk_temp()} C")
    print(f"HDD Disk: {hdd_temp()} C")

pass

if __name__=="__main__":
    test()

pass

