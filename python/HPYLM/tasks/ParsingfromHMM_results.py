#-*- coding: utf-8 -*-

import Restaurant
import dill

print("Start Parsing Test (from tmp/HMM_results.dill)")

rest = Restaurant.Restaurant(None, [])

# with open("tmp/HMM_results.dill", "rb") as f:
with open("tmp/log_MakerMain/dills/HMM_results.dill", "rb") as f:
    datas = dill.load(f)
u = []
"""
旧バージョン．methods で動作作ってた時の奴
for m in datas:
    for d in datas[m]:
        print(d)
        line = ""
        for s in d:
            line = line + rest.translate(s)
        u.append([line])
"""
for d in datas:
    print(datas[d])
    line = ""
    for s in datas[d]:
        line = line + rest.translate(s)
    u.append([line])

print("input sentences:")
for s in u:
    print(s[0])

result = rest.executeParsing(u, 1000000)

"""
旧バージョン
print("parsing results:")
with open("tasks/result.txt", "w") as f:
    for r in result:
        line = ""
        for w in r:
            line = line + w + ", "
        line = line + "\n"
        print(line)
        f.write(line)
"""
print("parsing results:")
for r in result:
    line = ""
    for w in r:
        line = line + w + ", "
    print(line)

with open("tmp/log_MakerMain/dills/HPYLM_results.dill", "wb") as f:
    dill.dump(result, f)
    print("Successfully dumping : result")
