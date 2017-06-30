#-*- coding: utf-8 -*-

import Restaurant

print("Start Parsing Test")

rest = Restaurant.Restaurant(None, [])

u = []

with open("tasks/inputSentences.txt", "r") as f:
    line = f.readline()
    while(line != ""):
        u.append(line[:-1])
        line = f.readline()

print("input sentences:")
for s in u:
    print(s)

rest.executeParsing(u, 100000)
