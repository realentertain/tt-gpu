#!/usr/bin/python3
import json
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm

hatches = ['//', '\\\\', '/', '\\', 'x', 'xx','o','O', '.']

class Block:
    def __init__ (self, kernel, nofThreads, start, end, smid, bid, offset=0):
        self.kernel = kernel
        self. nofThreads = nofThreads
        self.threadOffset = offset
        self.start = start
        self.end = end
        self.smid = smid
        self.id = bid
        self.maxThreadsOnSM = 2048

    def draw(self, ax, colors):
        thread_lower = self.threadOffset
        thread_upper = self.threadOffset + self.nofThreads
        ax.fill_between([self.start, self.end], [thread_upper, thread_upper], [thread_lower, thread_lower], facecolor=colors[self.kernel], alpha=0.25, hatch=hatches[self.kernel],edgecolor=colors[self.kernel],linewidth=1.0)
        
        ax.text(self.start+(self.end-self.start)/2,thread_lower+(thread_upper-thread_lower)/2,"K: "+str(self.kernel)+":"+str(self.id))



    def isOverlap(self, block):
        mythread_lower = self.threadOffset
        mythread_upper = self.threadOffset + self.nofThreads
        otherthread_lower = block.threadOffset
        otherthread_upper = block.threadOffset + block.nofThreads
        # Time overlap and thread overlap check
        if (block.end <= self.start) or (self.end <= block.start) or (otherthread_upper<=mythread_lower) or (mythread_upper <= otherthread_lower):
            print("K"+str(self.kernel)+":"+str(self.id)+" No overlap")
            # No overlap
            return False
        else:
            print("K"+str(self.kernel)+":"+str(self.id)+" Overlap")
            return True
    
    def getEnd(self):
        return self.end

    def getStart(self):
        return self.start

    def getSmid(self):
        return self.smid

    def getNofThreads(self):
        return self.nofThreads

    def getThreadOffset(self):
        return self.threadOffset
    
    def setThreadOffset(self, offset):
        if offset + self.nofThreads <= self.maxThreadsOnSM and offset >= 0:
            self.threadOffset = offset
    
    def incThreadOffset(self, amount):
        if self.threadOffset + self.nofThreads + amount <= self.maxThreadsOnSM:
            self.threadOffset += amount

def retrieveBlocksOfKernel(kernel, nofThreads, times, smid):
    # Split into start end times
    start_times = []
    stop_times = []
    for i in range(len(times)):
        if (i%2) == 0:
            start_times.append(times[i])
        else:
            stop_times.append(times[i])

    blocks = []
    for blockid in range(0,len(smid)):
            block = Block(kernel, nofThreads, times[2*blockid], times[2*blockid+1], smid[blockid], blockid)
            blocks.append(block)

    return blocks

def assignBlocksToSM(nofKernel, nofBlocks, nofThreads, blockTimes, smids, nofRepetitions=1):
    agg_sm = {}
    for kernel in range(0,nofKernel):

        # Get time subset of this blocks
        startindex = nofBlocks*kernel*nofRepetitions
        # Take only the first repetitions of blocktimes
        times = blockTimes[2*startindex:2*startindex+2*nofBlocks]
        smid = smids[startindex:startindex+nofBlocks]
        
        # Retrive the blocks of the kernel
        blocks = retrieveBlocksOfKernel(kernel, nofThreads, times, smid)
        # Put the retrived blocks to the according SM
        for block in blocks:
            if block.getSmid() not in agg_sm:
                agg_sm[block.getSmid()] = []
            agg_sm[block.getSmid()].append(block)
            print("K"+str(block.kernel)+":"+str(block.id) +" - Start|End " +str(block.start)+"|"+str(block.end)+ " Interval: "+str((block.end-block.start)*1e-9)+"s")
    return agg_sm
              

def findFreeSlot(occupied, block):
    offset = 0
    restart = True
    while restart:
        for block_fix in occupied:
            if block.isOverlap(block_fix):
                # We have some overlap int 2D space here
                block.incThreadOffset(block_fix.getNofThreads())
                # Restart the search
                restart = True
                break
            else:
                restart = False
    #print("Overlap K"+str(block.kernel)+":"+str(block.id)+" with K"+str(block_fix.kernel)+":"+str(block_fix.id)+ "Interval: "+str(interval)+"s")

def adjustThreadOffset(agg_sm):

    #Adjust the thread offset for the blocks on each SM
    for sm in agg_sm.keys():
        # Iterate through all blocks
        print("Adjust threads on SM " + str(sm))
        occupied = []
        for i, block in enumerate(agg_sm[sm]):
            if len(occupied) == 0:
                occupied.append(block)
                continue
            # Find appropriate slow
            findFreeSlot(occupied, block)

            #Store this block to occupied
            occupied.append(block)


def drawBlocks(agg_sm, nofKernel, minTime, maxTime):
    fig = plt.figure()
    fig.suptitle("Blocks scheduled on SM's")
    colors = cm.get_cmap('viridis', nofKernel).colors

    for i, sm in enumerate(agg_sm.keys()):
        ax = fig.add_subplot(2, 1, i+1)
        for block in agg_sm[sm]:
            block.draw(ax, colors)
        ax.set_ylabel("NofThreads")
        ax.set_yticks(range(0,2049,512))
        ax.set_xlabel("Time [s]")
        ax.set_title("SM "+str(i))


def drawScenario(filename):
    with open(filename) as f1:
        data = json.load(f1)

    nofThreads = int(data['nofThreads'])
    nofBlocks  = int(data['nofBlocks'])
    nofKernel  = int(data['nofKernel'])
    nofRep     = int(data['nof_repetitions'])
    dataSize   = int(data['data_size'])
    measOH     = int(data['measOH'])
    blockTimes = data['blocktimes']
    kernelTimes= data['kerneltimes']
    smids      = data['smid']

    blockTimes = [float(i)*1e-9 for i in blockTimes]
    kernelTimes = [float(i) for i in kernelTimes]
    smids = [int(i) for i in smids]

    minTime = min(blockTimes)
    maxTime = max(blockTimes)
    blockTimes= [i-minTime for i in blockTimes]

    agg_sm = assignBlocksToSM(nofKernel, nofBlocks, nofThreads, blockTimes, smids, nofRep)
    adjustThreadOffset(agg_sm)
    drawBlocks(agg_sm, nofKernel, minTime, maxTime)
if __name__ == "__main__":
    filename = "out/512t-2b-1k-4096.json"
    drawScenario(filename)
    plt.show()
