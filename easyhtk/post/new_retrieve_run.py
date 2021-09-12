#!/usr/bin/env python3

import sys
import time
import new_retrieve

start = time.time()

input_dir = sys.argv[1]
new_retrieve.retrieve(input_dir)

print(f'Running time: {time.time() - start} seconds')
