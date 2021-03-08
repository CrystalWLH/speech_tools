import os
import random
import sys


input_dir = sys.argv[1]
output_dir = sys.argv[2]
files = os.listdir(input_dir)

for file in files:
    ratio = random.uniform(0.8, 1.0)
    source = os.path.join(input_dir, file)
    target = os.path.join(output_dir, file)
    os.system('sox ' + source + ' ' + target + ' speed ' + str(ratio))
