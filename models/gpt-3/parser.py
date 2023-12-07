import re
import pickle
import numpy as np
import sys

RESULT_FILE = sys.argv[1]

with open(RESULT_FILE, 'rb+') as f:
    all_results = pickle.load(f)


count = {'A' : 0, 'B' : 0, 'C' : 0, 'D' : 0, 'E': 0,'UNK' : 0}
traits = {
    "O" : [],
    "C" : [],
    "E" : [],
    "A" : [],
    "N" : []
}

SCORES = {
    "A" : 5 , 
    "B" : 4 ,
    "C" : 3 ,
    "D" : 2 ,
    "E" : 1 ,
}

def calc_mean_and_var(result):
    mean  = {}
    std  = {}
    for key, item in result.items():
        mean[key] = np.mean(np.array(item))
        std[key] = np.std(np.array(item))

    return f'''mean:\n {sorted(mean.items(), key=lambda item:item[0])}\n std:\n {sorted(std.items(), key=lambda item:item[0])}'''

for question in all_results:
    res = question[2]['text'] + ')'
    choice = re.search(r'[abcdeABCDE][^a-zA-Z]', res, flags = 0).group()[0].upper()
    count[choice] += 1
    label = question[0]['label_ocean']
    label_raw = question[0]['label_raw']
    key = question[0]['key']
    score = SCORES[choice]

    if key == 1:
        traits[label].append(score)
    else:
        traits[label].append(6 - score)

print(calc_mean_and_var(traits))

print(count)
