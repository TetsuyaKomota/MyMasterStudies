# coding = utf-8

import glob
import os

dirs = glob.glob("*")

for d in dirs:
    if os.path.isdir(d) != True:
        continue
    os.mkdir("after/"+d)

    files = glob.glob(d+"/*")

    for f in files:
        if f[-4:] != ".csv":
            continue
        with open(f, "r", encoding="utf-8") as g:
            with open("after/"+f, "w", encoding="utf-8") as h:
                while True:
                    line = g.readline()
                    if line == "":
                        break
                    idx  = int(line.split(",")[0])
                    rest = ",".join(line.split(",")[1:])
                    h.write(str(idx-1)+","+rest)
