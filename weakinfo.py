#!/usr/bin/env python3
# extract (weak) block information from debug.log on stdin
# write space separated output with weak / strong block arrival times and further info
from sys import stdin, stderr
from datetime import datetime
import socket

# should be compatible with  logtimemicros=1 and ..=0
ntemplate_us  =len("1111-11-11 11:11:11.111111")
ntemplate_nous=len("1111-11-11 11:11:11")

microseconds = 0

def getTime(line):
    try:
        if microseconds:
            return datetime.strptime(line[:ntemplate_us], "%Y-%m-%d %H:%M:%S.%f").timestamp()
        else:
            return datetime.strptime(line[:ntemplate_nous], "%Y-%m-%d %H:%M:%S").timestamp()
    except Exception as e:
        return 0

already = {"0" * 64} # stuff that has already been seen

host = socket.gethostname()

if __name__ == "__main__":
    ws_block="0"*64

    for i, line in enumerate(stdin):
        ls=line.split()
        t = getTime(line)
        if t == 0:
            continue
        s=("%20s %17.6f " % (host, t))
        if "Processing new block" in line and "from peer" in line:
            ws_block = ls[5]

        elif line.endswith("Block is strong.\n"):
            if ws_block not in already:
                print((s+"%20s ") % "STRONG", end='')
                print(ws_block)
            already.add(ws_block)
            ws_block="0"*64

        elif line.endswith("Block is weak.\n"):
            if ws_block not in already:
                print((s+"%20s ") % "WEAK", end='')
                print(ws_block)
            already.add(ws_block)
            ws_block="0"*64

        elif "Found candidate weak block hash" in line:
            print((s+"%20s ") % "WEAK_POINTER", end='')
            print(ls[10][:64], ls[7])

        elif "Tracking weak block" in line:
            print((s+"%20s ") % "WEAK_STORE", end='')
            print(ls[5], "%8s" % ls[7])
        elif "UNEXPECTED INTERNAL PROBLEM" in line:
            print((s+"%20s ") % "MINER_PROBLEM")

        elif "Sent thinblock - size" in line:
            print((s+"%20s ") % "THIN_SEND", end='')
            print("%7s" % ls[6])

        elif "Sent regular block instead" in line:
            print((s+"%20s ") % "BLCK_SEND", end='')
            print("%7s" % ls[13])

        if (i%100000) == 0:
            print ("Until line", i, file=stderr)
