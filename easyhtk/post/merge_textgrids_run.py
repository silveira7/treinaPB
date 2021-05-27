#!/usr/bin/env python3

import sys
import time
import merge_textgrids

start = time.time()

input_dir = sys.argv[1]
textgrids = merge_textgrids.TextGrid(input_dir)
textgrids.get_metadata()
textgrids.build_tg()

print(f'Time: {time.time() - start} seconds.')
