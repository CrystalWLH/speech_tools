from pydub import AudioSegment
import os
import sys
import csv
import json
import pandas as pd
import argparse

def getStartEndDurDict(metadata_phone_dur):
    data = pd.read_csv('metadata_phone_dur.csv', sep='|', encoding='utf-8', quoting=csv.QUOTE_NONE)
    startEndDur = dict()
    index = list(range(data.shape[0]))
    
    for i in index:
        line = data.iloc[i]
        wav = line['wav']
        durList = line['phone_dur'].strip().split()
        startDur = float((int(durList[0]) + int(durList[1])) * 12.5)
        if 'punc' in  line['phone2'].strip().split()[-1]:
            endDur = float(int(durList[-1]) * 12.5)
        else:
            endDur = 0.0
        if wav in startEndDur.keys():
            print(wav + ' already existed in dictionary')
        else:
            startEndDur[wav] = tuple([startDur, endDur])

    return startEndDur


def rmStartEndDur(inputDir, outputDir, startEndDurDict):
    files = os.listdir(inputDir)
    for file in files:
        source = os.path.join(inputDir, file)
        target = os.path.join(outputDir, file)
        try:
            sound = AudioSegment.from_file(source, format="wav")
            startDur = int(startEndDurDict[file.replace('.wav', '')][0])
            endDur = int(startEndDurDict[file.replace('.wav', '')][1])
            duration = len(sound)
            rmStartEnd_sound = sound[startDur:duration-endDur]
            rmStartEnd_sound.export(target, format="wav")
        except:
            print(source)
    print('Rm start end duration successfully')

def addSilence(inputDir, outputDir, startSilence, endSilence):
    files = os.listdir(inputDir)
    for file in files:
        source = os.path.join(inputDir, file)
        target = os.path.join(outputDir, file)
        try:
            sound = AudioSegment.from_file(source, format="wav")
            startSil = AudioSegment.silent(duration=startSilence)
            endSil = AudioSegment.silent(duration=endSilence)
            addSil_sound = startSil + sound + endSil
            addSil_sound.export(target, format="wav")
        except:
            print(source)

    print('Add start and end silence sucessfully.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='remove start and end noise duration, add silence to start and end of waves.')
    parser.add_argument('--input_dir', help='input waves floder')
    parser.add_argument('--rmStartEnd_dir', help='rm start and end noise duration floder')
    parser.add_argument('--add_sil_dir', help='add silence to start and end of waves')
    parser.add_argument('--metadata_phone_dur', help='metadata phone duration file path')
    parser.add_argument('--startSilence', type=int, default=50, help='start silence length (ms)')
    parser.add_argument('--endSilence', type=int, default=100, help='end silence length (ms)')
    args = parser.parse_args()
    
    startEndDur = getStartEndDurDict(args.metadata_phone_dur)
    rmStartEndDur(args.input_dir, args.rmStartEnd_dir, startEndDur)
    addSilence(args.rmStartEnd_dir, args.add_sil_dir, args.startSilence, args.endSilence)
