#!/usr/bin/env python3


import sys
import time
import retrieve_waves

start = time.time()

input_dir = sys.argv[1]
original_waves = sys.argv[2]

retrieve_waves.batch_retrieve(input_dir, original_waves)

print(f'Time: {time.time() - start} seconds.')
