#!/usr/bin/python3

import os
import sys

# The kernel export uses BCM pin numbering. Make sure pins are exported.
for p in [17,18,27,22,23,24,25,4,2,3,8,7,10,9,11,14,15,5,6,13,19,26,12,16,20,21,0,1]:
    path = "/sys/class/gpio/gpio{0}".format(p);
    if os.path.isdir(path):
        f = open("/sys/class/gpio/unexport", "w")
        print("Removing " + path, file=sys.stderr)
        f.write("{0}\n".format(p))
        f.flush()
        f.close()
