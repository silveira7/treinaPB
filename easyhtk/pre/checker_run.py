import sys
import time
import checker

start = time.time()

input_dir = sys.argv[1]
output_dir = sys.argv[2]
checker.checker(input_dir, output_dir)

print(f'Tempo de execução: {time.time() - start} segundos.')
