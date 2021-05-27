#!/usr/bin/env python3

import sys
import time
import final_clean

start = time.time()

input_dir = sys.argv[1]
final_clean.final_clean(input_dir)

print(f'Time: {time.time() - start} seconds.')
