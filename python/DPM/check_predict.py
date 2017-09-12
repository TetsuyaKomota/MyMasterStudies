# coding = utf-8

import dill

with open("tmp/log_MakerMain/dills/predictMatching_results.dill", "rb") as f:
    datas = dill.load(f)

output = []

while True:
    if len(datas) == 0:
        break
    temp = 0
    idx = -1
    for i, d in enumerate(datas):
        Sum = 0
        for s in d["before"]:
            Sum += s["step"]
        Sum /= len(d["before"])
        if temp > Sum:
            temp = Sum
            idx = i
    output.append(datas.pop(idx))

datas = output
output = []

while True:
    if len(datas) == 0:
        break
    temp = 0
    idx = -1
    for i, d in enumerate(datas):
        print(len(d["before"]))
        if temp < len(d["before"]):
            print("HIT")
            temp = len(d["before"])
            idx = i
    output.append(datas.pop(idx))

for d in output:
    print("---")
    line = ""
    for i, p in enumerate(d["before"]):
        line += str(p["step"]) + " "
        if i%20 == 0 and i != 0:
            line += "\n"
    print(line+"\n")
