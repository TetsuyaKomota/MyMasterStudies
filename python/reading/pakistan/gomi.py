# coding = utf-8

"""
with open("newdata.csv", "w", encoding="utf-8") as output:
    with open("data.csv", "r", encoding="utf-8") as f:
        output.write(f.readline())
        count = 0
        temp = ""
        while True:
            count += 1
            line = f.readline()
            if line == "":
                break
            if line.split(",")[0].isdigit() == False or int(line.split(",")[0]) != count:
                temp = temp[:-1] + line
                count -= 1
            else:
                if temp != "":
                    output.write(temp)
                temp = line
"""

with open("tmp/result_scatter.csv", "w", encoding="utf-8") as output:
    with open("tmp/result.csv", "r", encoding="utf-8") as f:
        sc = {}
        for i in range(10, 21):
            sc[i] = {}
        print(sc)
        while True:
            line = f.readline()[:-1].split(",")
            if len(line) < 2:
                break
            sc[int(line[0])][int(line[1])] = int(line[2])
    output.write(",")
    for k in sorted(list(sc.keys())):
        output.write(str(k)+",")
    output.write("\n")
    for i in sorted(list(sc[10].keys())):
        output.write(str(i)+",")
        for k in sc.keys():
            output.write(str(sc[k][i])+",")
        output.write("\n")

