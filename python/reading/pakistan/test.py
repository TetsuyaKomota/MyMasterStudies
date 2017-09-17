# coding = utf-8

# とりあえずデータを見てみよう
# 自爆テロを時系列順に並べて，発生場所を HMM で予測してみよう

import re 


def readCSV(path):
    output = {}
    index = []
    with open(path, "r", encoding="utf-8") as f:
        index = f.readline()[:-1].split(",")
        for l in index:
            output[l] = []
        while True:
            line = f.readline()
            if line == "":
                break
            for i, l in enumerate(index):
                output[l].append(line.split(",")[i])
    return output

# Date がうんこなので書き換える
def changeDate(datas):
    c = []
    tbl = {}
    tbl["January"] = 1
    tbl["Jan"] = 1
    tbl["February"] = 2
    tbl["Feb"] = 2
    tbl["March"] = 3
    tbl["Mar"] = 3
    tbl["April"] = 4
    tbl["Apr"] = 4
    tbl["May"] = 5
    tbl["May"] = 5
    tbl["June"] = 6
    tbl["Jun"] = 6
    tbl["July"] = 7
    tbl["Jul"] = 7
    tbl["August"] = 8
    tbl["Aug"] = 8
    tbl["September"] = 9
    tbl["Sep"] = 9
    tbl["October"] = 10
    tbl["Oct"] = 10
    tbl["November"] = 11
    tbl["Nov"] = 11
    tbl["December"] = 12
    tbl["Dec"] = 12
    for i,d in enumerate(datas["Date"]):
        print(i)
        d = re.sub(" ", "-", d)
        # 曜日-月-日-年 となっている
        ye = int(d.split("-")[-1])
        mo = tbl[d.split("-")[1]]
        da = int(d.split("-")[2])
        c.append(int("{0:04d}".format(ye)+"{0:02d}".format(mo)+"{0:02d}".format(da)))
    datas["Date"] = c
    return datas

if __name__ == "__main__":
    data = readCSV("tmp/data.csv")
    data = changeDate(data)
    size = len(data["S#"])
    temp = 0
    for s in range(size):
        if temp > data["Date"][s]:
            print("しね")
            print(data["Date"][s])
            break
        temp = data["Date"][s]
        print(str(s) + "\t:" + str(data["Date"][s]) + "\t\t\t\t:" + data["Latitude"][s] + "\t\t\t\t:" + data["Longitude"][s])
