#!/usr/bin/env python3

import sys
import time
import orthography

start = time.time()

input_dir = sys.argv[1]
ou_exceptions = sys.argv[2]
r_exceptions = sys.argv[3]

orthography.change(input_dir, ou_exceptions, r_exceptions)

print(f'Time: {time.time() - start} seconds.')
