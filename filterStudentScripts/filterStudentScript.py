import os
import sys
import argparse
import re

illegal_pattern = r'[0-9@&#*+$•|©`®×ø=ïíáéñàó]'

def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--inputScipt',
        dest='inputscipt',
        default=None)
    parser.add_argument(
        '--outputScript',
        dest='outputscript',
        default=None)
    
    args, _ = parser.parse_known_args()
    return args


def getCharSet(inputfile, outputfile):
    with open(inputfile, 'r', encoding='utf-8') as f_in:
        lines = f_in.readlines()
    chars = dict()
    for line in lines:
        line = line.strip()
        if len(line) == 0:
            continue
        line = line.replace(' ', '')
        for char in line:
            if char not in chars.keys():
                chars[char] = 1
            else:
                chars[char] = chars[char] + 1
    chars_sorted = sorted(chars.items(), key=lambda x: x[1], reverse=True)

    f_out = open(outputfile, 'w', encoding='utf-8')
    for item in chars_sorted:
        f_out.write(item[0] + '\t' + str(item[1]) + '\n')
    f_out.close()


def filterScript(inputscipt, outputscript):
    with open(inputscipt, 'r', encoding='utf-8') as f_in:
        lines = f_in.readlines()
    
    count = 0
    print('There are ' + str(len(lines)) + ' in original file.')
    f_out = open(outputscript, 'w', encoding='utf-8')
    for line in lines:
        line = line.strip()
        if len(line) == 0:
            continue
        if re.findall(illegal_pattern, line):
            continue
        line = ' '.join(line.split()).strip()
        f_out.write(line + '\n')
        count = count + 1
    print('There are ' + str(count) + ' in processed file.')
    f_out.close()

if __name__ == "__main__":
    args = get_arguments()
    inputscipt = args.inputscipt
    outputscript = args.outputscript
    filterScript(inputscipt, outputscript)
