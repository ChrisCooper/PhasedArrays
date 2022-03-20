#!/usr/bin/python

import numpy as np
import time
import os

os.system("taskset -p 0xffffffff %d" % os.getpid())

np_start = time.time()
for i in range(1000):
    tmp = np.random.rand(2000,2000) ** 6
np_end = time.time()

print(f"time: {(np_end-np_start):0.4}s")

