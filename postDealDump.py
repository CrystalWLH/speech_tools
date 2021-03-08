
f_out = open('unitts_test.phone.txt', 'w', encoding='utf-8')

lines = open('test.phone.txt', 'r', encoding='utf-8').readlines()

for line in lines:
    line = line.strip()
    if line.endswith(' ~'):
        line = line[:-2]
    if line.endswith(' /'):
        line = line[:-2]
    line_unitts = line.replace('letter', 'xx-xx_letter')
    f_out.write('<BOS> / ' + line_unitts + '\n')

f_out.close()
