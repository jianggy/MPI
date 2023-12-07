import pandas as pd
import numpy as np

ay = []
path = "./IPIP120.dat"
col_list = ["label_ocean"]


def split(word):
    return [int(char) for char in word]


df_label = pd.read_csv("../inventories/mpi_120.csv", usecols=col_list)
with open(path, "r") as f:
    line = f.readline()
    while line is not None:
        line = f.readline()
        arl = split(line[-121:-1])
        if len(arl) != 120:
            break
        ay.append(arl)

ppl_mean = {}
ppl_std = {}
for dimension in ["O", "C", "E", "A", "N"]:
    rid = list(df_label.loc[df_label["label_ocean"] == dimension].index)
    arr = np.array(ay)
    arrd = arr[:, rid]
    ppl_mean[dimension] = arrd.mean(axis=1).mean()
    ppl_std[dimension] = arrd.std(axis=1).mean()

print(ppl_mean)
print(ppl_std)

"""
mean: {'O': 3.4405334983986084, 'C': 3.604337364673124, 'E': 3.4112817216318954, 'A': 3.6591013094855462, 'N': 2.8051019759917772}
var: {'O': 1.1304017283918237, 'C': 0.9782270902644087, 'E': 1.0657034983508744, 'A': 1.0361185583233663, 'N': 1.055805943496183}
This result (var) might differ from the result in the paper due to numerical stability (averaging ~600k individual results).
"""
