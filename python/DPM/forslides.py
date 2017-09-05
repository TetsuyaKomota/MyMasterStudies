# coding = utf-8

import DPM.ViewPointEncoder as encoder
import DPM.ViewPointManager as manager

interList = []
path="tmp/log_MakerMain/GettingIntermediated/3-2500-2500-9/inter000000000.csv"
with open(path) as f:
    while True:
        line = f.readline()
        if line == "":
            break
        interList.append(int(line.split(",")[0]))
print("inters:"+str(interList))

with open("tmp/log_MakerMain/log000000000.csv", "r", encoding="utf-8") as f:
    counter = 0
    while True:
        counter+=1
        line = f.readline()
        if line == "":
            break
        elif counter%6 != 0 and counter not in interList:
            continue
        state = encoder.encodeState(line)
        name = "log000000000_"+str(counter)+".png"
        inter = counter in interList
        manager.savefig(state, name=name, log=True, inter=inter)
