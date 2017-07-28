#-*- coding: utf-8 -*-

import Restaurant

print("Start Parsing Test")

rest = Restaurant.Restaurant(None, [])

u = []

with open("HPYLM/tasks/inputSentences.txt", "r") as f:
    line = f.readline()
    while(line != ""):
        u.append([line[:-1]])
        line = f.readline()

print("input sentences:")
for s in u:
    print(s[0])

result = rest.executeParsing(u, 100000)

print("parsing results:")
with open("tasks/result.txt", "w") as f:
    for r in result:
        line = ""
        for w in r:
            line = line + w + ", "
        line = line + "\n"
        print(line)
        f.write(line)

