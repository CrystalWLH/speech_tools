import os
import sys
import argparse
import re

compile_patterns = lambda patterns: [(re.compile(pattern), repl) for pattern, repl in patterns]

# Farsi punctuation
punc_after, punc_before = r'\.:!،؛؟»\]\)\}', r'«\[\(\{'
punc_list = [r'.', r':', r'!', r'،', r'؛', r'؟', r'«', r'»', r'[', r']', r'(', r')', r'{', r'}', r';', r'…', r'٬', r'"']

# Punctuation pattern
punctuation_spacing_patterns = compile_patterns([
    ('" ([^\n"]+) "', r'"\1"'),
    ('([\S])(['+ punc_after +'])', r'\1 \2'),
    ('(['+ punc_before +'])(.)', r'\1 \2'),
    ('(['+ punc_after[:3] +'])([^ '+ punc_after +'\d])', r'\1 \2'),
    ('(['+ punc_after[3:] +'])([^ '+ punc_after +'])', r'\1 \2'),
    ('([^ '+ punc_before +'])(['+ punc_before +'])', r'\1 \2'),
])

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


def punctuation_spacing(text, punctuation_spacing_patterns):
    for pattern, repl in punctuation_spacing_patterns:
        text = pattern.sub(repl, text)
    return text

def punctuation_addspace(text, punc_list):
    processed_text = text
    for item in punc_list:
        processed_text = processed_text.replace(item, " {} ".format(item))
    return processed_text

def process_file(inputscipt, outputscript, punctuation_spacing_patterns, punc_list):
    with open(inputscipt, 'r', encoding='utf-8') as f_in:
        lines = f_in.readlines()

    f_out = open(outputscript, 'w', encoding='utf-8')
    for line in lines:
        line = line.strip()
        #processedLine = punctuation_spacing(line, punctuation_spacing_patterns)
        processedLine = punctuation_addspace(line, punc_list)
        processedLine = ' '.join(re.split(' +|\n+', processedLine))
        f_out.write(processedLine.strip() + '\n')
    f_out.close()

    print('Texts processing done!')

if __name__ == "__main__":
    args = get_arguments()
    inputscipt = args.inputscipt
    outputscript = args.outputscript
    process_file(inputscipt, outputscript, punctuation_spacing_patterns, punc_list)

