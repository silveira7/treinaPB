#!/usr/bin/env python3

import sys
import time
import make_vv_tier

start = time.time()

input_dir = sys.argv[1]
make_vv_tier.create_vv_tier(input_dir)

print(f'Time: {time.time() - start} seconds.')
