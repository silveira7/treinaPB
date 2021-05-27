#!/usr/bin/env python3

import sys
import time
import sample_chunks_by_size

start = time.time()

input_dir = sys.argv[1]
sample_chunks_by_size.sample_chunks(input_dir)

print(f'Time: {time.time() - start} seconds.')
