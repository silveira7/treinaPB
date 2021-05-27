#!/usr/bin/env python3

import sys
import time
import small_isolated

start = time.time()

input_dir = sys.argv[1]
small_isolated.delete_small_isolated(input_dir)

print(f'Time: {time.time() - start} seconds.')
