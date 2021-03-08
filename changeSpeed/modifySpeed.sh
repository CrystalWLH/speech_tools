#!/bin/bash

input_dir=$1
output_dir=$2

files=$(ls $input_dir)

for filename in $files
do
    input_path=$input_dir/$filename
    output_path=$output_dir/$filename
    sox $input_path $output_path speed 0.8
done


