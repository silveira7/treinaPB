import sys
import cleaner
import wordlist

input_dir = sys.argv[1]
output_dir = sys.argv[2]

labs = cleaner.get_labs(input_dir)
cleaner.delete_empties(labs, input_dir)

