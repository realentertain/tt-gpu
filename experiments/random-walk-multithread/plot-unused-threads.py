#!/usr/bin/python3
import json
import matplotlib.pyplot as plt
import numpy as np




filename1 = "out-unused-threads/256-cg-threads-different-elem.json"
filename2 = "out-unused-threads/10-cg-threads-different-elem.json"
filename3 = "out-unused-threads/5-cg-threads-different-elem.json"
filename4 = "out-unused-threads/3-cg-threads-different-elem.json"
filename5 = "out-unused-threads/2-cg-threads-different-elem.json"
filename6 = "out-unused-threads/1-cg-threads-different-elem.json"
filename7 = "out-unused-threads/256-cg-threads-same-elem.json"

with open(filename1) as f1:
    data1 = json.load(f1)
with open(filename2) as f2:
    data2 = json.load(f2)
with open(filename3) as f3:
    data3 = json.load(f3)
with open(filename4) as f4:
    data4 = json.load(f4)
with open(filename5) as f5:
    data5 = json.load(f5)
with open(filename6) as f6:
    data6 = json.load(f6)
with open(filename7) as f7:
    data7 = json.load(f7)

# red dashes, blue squares and green triangles
plt.plot(data1['nof_threads'], data1['mean'],'r')
plt.plot(data2['nof_threads'], data2['mean'],'g')
plt.plot(data3['nof_threads'], data3['mean'],'b')
plt.plot(data4['nof_threads'], data4['mean'],'c')
plt.plot(data5['nof_threads'], data5['mean'],'m')
plt.plot(data6['nof_threads'], data6['mean'],'k')
plt.plot(data7['nof_threads'], data7['mean'],'y')
plt.gca().legend(('256k, threads, different element',\
                  '10k, threads, different element',\
                  '5k, threads, different element',\
                  '3k, threads, different element',\
                  '2k, threads, different element',\
                  '1k, threads, different element',\
                  '256k, threads, same element'))
plt.fill_between(data1['nof_threads'], data1['min'], data1['max'], facecolor='red', alpha=0.5)
plt.fill_between(data2['nof_threads'], data2['min'], data2['max'], facecolor='green', alpha=0.5)
plt.fill_between(data3['nof_threads'], data3['min'], data3['max'], facecolor='blue', alpha=0.5)
plt.fill_between(data4['nof_threads'], data4['min'], data4['max'], facecolor='cyan', alpha=0.5)
plt.fill_between(data5['nof_threads'], data5['min'], data5['max'], facecolor='magenta', alpha=0.5)
plt.fill_between(data6['nof_threads'], data6['min'], data6['max'], facecolor='black', alpha=0.5)
plt.fill_between(data7['nof_threads'], data7['min'], data7['max'], facecolor='yellow', alpha=0.5)
#plt.axis([1,1024 , 0, 370])
plt.xticks(np.arange(0, 1025, step=64))
#plt.semilogx(datal1['size'], np.sin(2*np.pi*np.asarray(datal1['size'])))
plt.grid(True, which="both")
plt.title('Random walk - L2')
plt.xlabel('Nof Threads')
plt.ylabel('Cycles/Elem')
plt.show()
