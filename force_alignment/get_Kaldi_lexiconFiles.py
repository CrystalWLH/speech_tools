import csv, json
import pandas as pd
import argparse

def getTextFile(inputCSV, output, prefix):
    data = pd.read_csv(inputCSV, sep='|', encoding='utf-8', quoting=csv.QUOTE_NONE)
    f_out = open(output, 'w', encoding='utf-8')
    txt_new = list()
    index = list(range(data.shape[0]))
    for i in index:
        item = data.iloc[i]
        line = item['phone2']
        wav = item['wav']
        line = line.strip().replace('<BOS> / ', '')
        new_line = ""
        wordList = line.split('/')
        for word in wordList:
            phoneList = word.strip().split()
            if len(phoneList) == 1 and 'punc' in phoneList[0]:
                new_line = new_line + phoneList[0].replace('punc', '') + ' '
            else:
                new_word = ""
                for phone in phoneList:
                    new_word = new_word + phone.replace(prefix, '')
                new_line = new_line + new_word.strip() + ' '

        f_out.write(wav + ' ' + new_line.strip() + '\n')
        txt_new.append(new_line.strip())
    
    f_out.close()
    data['txt_new'] = txt_new
    print('Get text file successfully.')
    return data

def getLexicon(data, output):
    dictionary = dict()
    f_out = open(output, 'w', encoding='utf-8')
    index = list(range(data.shape[0]))
    for i in index:
        line = data.iloc[i]
        phones = line['phone2']
        text = line['txt_new']

        phone_list = phones.strip().split('/')[1:]
        text_list = text.strip().split()
        if len(phone_list) != len(text_list):
            print('The length of phone sequence is not equal with the length of word sequence')
            continue
        for key, value in zip(text_list, phone_list):
            key = key.strip()
            value = value.strip()
            if key in dictionary.keys():
                if dictionary[key] != value:
                    print('Error lexicon: ' + str(key))
                    continue
            else:
                dictionary[key] = value 
    
    for key, value in dictionary.items():
        f_out.write(key.strip() + ' ' + value.strip() + '\n')
    f_out.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get some lexicon and text files to force aligm with kaldi')
    parser.add_argument('--inputCSV', default='merged_metadata_unitts.csv', help='input metadata_phone.csv file name')
    parser.add_argument('--outputText', default='text', help='output text file name')
    parser.add_argument('--outputLexicon', default='lexicon.txt', help='output lexicon file name')
    parser.add_argument('--prefix', default='et-ee_letter_', help='prefix of char need to be removed')
    args = parser.parse_args()
    data = getTextFile(args.inputCSV, args.outputText, args.prefix)
    getLexicon(data, args.outputLexicon)
