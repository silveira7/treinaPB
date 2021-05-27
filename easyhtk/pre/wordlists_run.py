#!/usr/bin/env python3

import sys
import wordlists
import time

start = time.time()

input_dir = sys.argv[1]
output_dir = sys.argv[2]

wordlists.wordlists(input_dir, output_dir)

print(f"Time: {time.time() - start}")
