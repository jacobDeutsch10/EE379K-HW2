import sysfs_paths as sysfs
import subprocess
import time
import telnetlib as tel
import psutil

def getTelnetPower(SP2_tel, last_power):
    tel_dat = str(SP2_tel.read_very_eager())
    print("telnet reading:", tel_dat)
    findex = tel_dat.rfind('\n')
    findex2 = tel_dat[:findex].rfind('\n')
    findex2 = findex2 if findex2 != -1 else 0
    ln = tel_dat[findex2: findex].strip().split(',')
    if len(ln) < 2:
        total_power = last_power
    else:
        total_power = float(ln[-2])
    return total_power

def getCpuLoad():
    return [x/100 for x in psutil.cpu_percent(interval=None, percpu=True)]

def getTemps():
    temp1 = []
    for i in range(4):
        temp =  float(file(sysfs.fn_thermal_sensor.format(i), 'r').readline().strip())/1000
        temp1.append(temp)
    t1=temp1[3]
    temp1[3] = temp1[1]
    temp1[1] = t1
    return temp1
        
def getAvailFreqs(cluster):
    freqs = open(sysfs.fn_cluster_freq_range.format(cluster)).read().strip().split(' ')
    return [int(f.strip()) for f in freqs]

def getClusterFreq(cluster):
    with open(sysfs.fn_cluster_freq_read.format(cluster), 'r') as f:
        return int(f.read().strip())

def setUserSpace(clusters=None):
    print("setting userspace")
    clusters = [0,4]
    for i in clusters:
        with open(sysfs.fn_cluster_gov.format(i), 'w') as f:
            f.write('userspace')
def setClusterFreq(cluster_num, frequency):
    """
        freq in khz
        0: little cluster
        4: big cluster
    """
    with open(sysfs.fn_cluster_freq_set.format(cluster_num), 'w') as f:
        f.write(str(frequency))


print getAvailFreqs(0)
print getAvailFreqs(4)

setUserSpace()
setClusterFreq(0, 200000)
print getClusterFreq(0)
setClusterFreq(4, 2000000)
print getClusterFreq(4)
out_fname = "problem1-3_bodytrack.txt"
header = "time V A W W/h usage_c0 usage_c1 usage_c2 usage_c3 usage_c4 usage_c5 usage_c6 usage_c7 temp_c4 temp_c5 temp_c6 temp_c7, frequency"
header = "\t".join(header.split(' '))
out_file = open(out_fname, 'w')
out_file.write(header)
out_file.write('\n')
#command = "taskset --all-tasks 0xF0 blackscholes 1 in_10M_blackscholes.txt blackscholes_out.txt"

DELAY = 0.2
SP2_tel = tel.Telnet('192.168.4.1')
total_power = 0.0
#subprocess.Popen(command.split(' '))
for i in range(6000):
    start = time.time()
    
    total_power = getTelnetPower(SP2_tel, total_power)
    print("telnet power: ", total_power)
    
    usage = getCpuLoad()
    print("usage: ", usage)
    freq = getClusterFreq(4)
    print("freq: ", freq)
    temps = getTemps()
    print("temps: ", temps)
    time_stamp = start
    fmt_str = '{}\t'*15
    out = fmt_str.format(time_stamp, total_power, usage[0], usage[1],\
    usage[2], usage[3], usage[4], usage[5], usage[6],usage[7],\
    temps[0], temps[1], temps[2], temps[3], freq)
    out_file.write(out)
    out_file.write('\n')
    elapsed = time.time()-start
    time.sleep(max(0, DELAY-elapsed))
    
    
    
    
    
    
    
    
    
