mp3dir=$1
wavdir=$2

f=`ls $mp3dir | awk -F'.' '{print $1}'`

for i in $f;do
  ffmpeg -i $mp3dir/$i.mp3 -ac 1 -ar 16000 $wavdir/$i.wav
done