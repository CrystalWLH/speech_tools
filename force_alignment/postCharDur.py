import os
import sys
import csv
import json
import pandas as pd


def combineBreakSil(lines):
    resultList = list()
    
    isnotDone = False
    isnotDoneBOS = False
    previousphone = ''
    previousDur = 0.0
    previousTime = 0
    previousKey = lines[0].strip().split()[0]

    sil_list = {'1', '2', '3', '4', '5'}
    BOS_list = {'138', '139', '140', '141'}
    break_sil_list = {'138', '139', '140', '141', '1', '2', '3', '4', '5'}
    
    if len(lines) >= 2 and lines[0].strip().split()[-1] in sil_list and lines[1].strip().split()[-1] in BOS_list:
        dur = float(lines[0].strip().split()[3]) + float(lines[1].strip().split()[3])
        time = float(lines[0].strip().split()[2])
        phone = lines[1].strip().split()[-1]
        resultList.append(int(dur * 80))
        lines = lines[2:]

    for line in lines:
        key = line.strip().split()[0]
        if key != previousKey:
            print('Error: The key is not same ' + str(key))
        phone = line.strip().split()[-1]
        dur = float(line.strip().split()[3])
        time = float(line.strip().split()[2])

        if phone in break_sil_list and not isnotDone:
            isnotDone = True
            previousphone = phone
            previousTime = time
            previousDur = dur
        elif phone in break_sil_list and isnotDone:
            previousDur = previousDur + dur
        elif isnotDone:
            isnotDone = False
            resultList.append(int(previousDur * 80))
            resultList.append(int(dur * 80))
            #resultList.append(str(previousTime) + ' ' + str(round(previousDur, 3)) + ' ' + str(previousphone))
            #resultList.append(str(time) + ' ' + str(round(dur, 3)) + ' ' + str(phone))
        else:
            resultList.append(int(dur * 80))
            #resultList.append(str(time) + ' ' + str(round(dur, 3)) + ' ' + str(phone))

    return resultList

def dealTotalSentence(inputFile):
    lines = open(inputFile, 'r', encoding='utf-8').readlines()
    resultDict = dict()
    sentenceDict = dict()
    for line in lines:
        key = line.strip().split()[0]
        if key not in sentenceDict.keys():
            sentenceDict[key] = list()
            sentenceDict[key].append(line)
        else:
            sentenceDict[key].append(line)

    for key, values in sentenceDict.items():
        lineResult = combineBreakSil(values)
        resultDict[key] = lineResult

    print('There are ' + str(len(resultDict)) + ' sentences')
    return resultDict

def getDurMetadata(inputMetadata, outputMetadata, durationDict):
    data_df = pd.read_csv(inputMetadata, sep='|', encoding='utf-8', quoting=csv.QUOTE_NONE)
    data = pd.DataFrame(columns = ['', 'Unnamed: 0', 'style_id', 'wav', 'locale_id', 'speaker_id', 'txt2', 'phone', 'phone2', 'phone_dur'])
#    data['style_id'] = data_df['style_id']
#    data['wav'] = data_df['wav']
#    data['locale_id'] = data_df['locale_id']
#    data['speaker_id'] = data_df['speaker_id']
#    data['txt2'] = data_df['txt2']
#    data['phone'] = data_df['phone2']
#    data['phone2'] = data_df['phone2']
    index = list(range(data_df.shape[0]))
#    data[''] = index
#    data['Unnamed: 0'] = index
#    durations = list()
    count = 0
    for i in index:
        line = data_df.iloc[i]
        wav = line['wav']
        if wav not in durationDict.keys():
            print(str(wav) + ' not in dictionary.')
            continue
        durationList = durationDict[wav]
        if len(durationList) != len(line['phone2'].strip().split()):
            print('Error: Phone sequence length is not as same as the length of duration' + str(i) + ' ' + line['wav'])
            continue
        durationSeq = ' '.join('%s' %id for id in durationList).strip()
        sample = pd.Series([count, count, line['style_id'], wav, line['locale_id'], line['speaker_id'], line['txt2'], line['phone2'].strip(), line['phone2'].strip(), durationSeq], index=data.columns)
        data = data.append(sample, ignore_index=True)
        count = count + 1

    data.to_csv(outputMetadata, sep='|', encoding='utf-8', index=False, quoting=csv.QUOTE_NONE)

durationDict = dealTotalSentence('swke_aikuma_4/all.ctm')
getDurMetadata('swke_aikuma_4/metadata_phone.csv', 'swke_aikuma_4/metadata_phone_dur.csv', durationDict)
