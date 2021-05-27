#!/usr/bin/env python3

import sys
import time
import broken_encoding

start = time.time()

input_dir = sys.argv[1]
broken_encoding.fix_encoding(input_dir)

print(f'Time: {time.time() - start} seconds.')
