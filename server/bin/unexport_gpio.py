#!/usr/bin/python3

import os
import sys

# The kernel export uses BCM pin numbering. Make sure pins are exported.
for p in [4,5,6,12,13,16,17,18,19,20,21,22,23,24,25,26,27]:
    path = "/sys/class/gpio/gpio{0}".format(p);
    if os.path.isdir(path):
        f = open("/sys/class/gpio/unexport", "w")
        print("Removing " + path, file=sys.stderr)
        f.write("{0}\n".format(p))
        f.flush()
        f.close()
