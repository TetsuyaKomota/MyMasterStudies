# coding = utf-8

import dill

with open("tmp/log_MakerMain/dills/DP_main_temp.dill", "rb") as f:
    d = dill.load(f)

for D in d:
    line = ""
    for i in range(len(D["before"])):
        if D["isadd"][i] == True:
            line += "**"
        line += D["after"][i]
        line += "\t"
    print(line)

for D in d:
    b = 0
    a = 0
    for i in range(len(D["before"])):
        b += D["before"][i]
        a += D["after"][i]
    b /= len(D["before"])
    a /= len(D["before"])
    print(str(b) + " - " + str(a))
