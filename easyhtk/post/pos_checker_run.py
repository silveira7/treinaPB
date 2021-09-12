#!/usr/bin/env python3

import sys
import time
import pos_checker

start = time.time()

input_dir = sys.argv[1]
pos_checker.check(input_dir)

print(f'Running time: {time.time() - start} seconds.')
