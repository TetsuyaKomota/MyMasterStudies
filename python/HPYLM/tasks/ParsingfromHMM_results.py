#-*- coding: utf-8 -*-

import Restaurant
import dill

print("Start Parsing Test (from tmp/HMM_results.dill)")

rest = Restaurant.Restaurant(None, [])

with open("../tmp/HMM_results.dill", "rb") as f:
    datas = dill.load(f)
u = []
for m in datas:
    for d in datas[m]:
        print(d)
        line = ""
        for s in d:
            line = line + rest.translate(s)
        u.append([line])

print("input sentences:")
for s in u:
    print(s[0])

result = rest.executeParsing(u, 100000)

print("parsing results:")
with open("tasks/resultfromHMM_results.txt", "w") as f:
    for r in result:
        line = ""
        for w in r:
            line = line + w + ", "
        line = line + "\n"
        print(line)
        f.write(line)

