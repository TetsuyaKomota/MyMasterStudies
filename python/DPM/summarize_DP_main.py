# coding = utf-8

import dill
import matplotlib.pyplot as plt

with open("tmp/log_MakerMain/dills/DP_main_temp.dill", "rb") as f:
    d = dill.load(f)

flist = d[0]["fname"][:25]

line = ""
for l in flist:
    line += l[8:12]
    line += "\t"
print(line)

for D in d:
    line = ""
    # for i in range(len(D["before"])):
    for fname in flist:
        i = D["fname"].index(fname)
        if D["isadd"][i] == True:
            line += "**"
        line += str(D["after"][i]["step"])
        line += "\t"
    print(line)

for D in d:
    b = 0
    a = 0
    for i in range(len(D["before"])):
        b += D["before"][i]["step"]
        a += D["after"][i]["step"]
    b /= len(D["before"])
    a /= len(D["before"])
    print(str(int(b)) + " - " + str(int(a)))

alist = []
for D in d:
    alist.append([a["step"] for a in D["after"]])

plt.xlim(0,500)
I = 3
for i in range(I):
    temp = []
    L = int(len(alist)/I)
    for j in range(L):
        temp += alist[L*i+j]
    plt.hist(temp, bins = 75)
plt.show()
plt.close()
