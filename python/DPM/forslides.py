# coding = utf-8

import DPM.ViewPointEncoder as encoder
import DPM.ViewPointManager as manager

with open("tmp/log_MakerMain/log000000000.csv", "r", encoding="utf-8") as f:
    counter = 0
    while True:
        counter+=1
        line = f.readline()
        if line == "":
            break
        elif counter%6 != 0:
            continue
        state = encoder.encodeState(line)
        name = "log000000000_"+str(counter)+".png"
        manager.savefig(state, name=name, log=False)
