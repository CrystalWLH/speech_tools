input_dir=$1
output_dir=$2

files=$(ls $input_dir)

for filename in $files
do
    input_path=$input_dir/$filename
    output_path=$output_dir/$filename
    sox $input_path $output_path norm -3
done
