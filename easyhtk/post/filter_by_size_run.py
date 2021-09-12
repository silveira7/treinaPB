#!/usr/bin/env python3

import sys
import time
import filter_by_size

start = time.time()

input_dir = sys.argv[1]
filter_by_size.filter(input_dir)

print(f'Time running: {time.time() - start} seconds.')
