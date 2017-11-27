# coding = utf-8

# summarize_DP_main で作った results.csv をパラメータごとに集計する
def execute(x=0, y=1):

    xy = "[" + str(x) + "," + str(y) + "]"

    output = {}

    dirpath  = "tmp/MAJIDEMAINNOSYUUKEISURUNODA_results/"

    filepath = dirpath + "result.csv"
    with open(filepath, "r", encoding="utf-8") as f:
        # 各データの件名は
        # ~~~~/***-***-***-***
        # となっている
        count = 0
        while True:
            line = f.readline()
            if line == "":
                break
            count += 1
            title     = line.split(",")[0].split("/")[-1]
            paramList = title.split("-")
            p = line.split(",")[1]
            r = line.split(",")[2]
            F = line.split(",")[3]
            X = float(paramList[x])
            Y = float(paramList[y])
            if X not in output.keys():
                output[X] = {}
            for allX in output.keys():
                if Y not in output[allX].keys():
                    output[allX][Y] = {"p":[], "r":[], "F":[]}
            output[X][Y]["p"].append(float(p))
            output[X][Y]["r"].append(float(r))
            output[X][Y]["F"].append(float(F))

    # precision, recall, F ごとに別ファイルに書き出しする
    filepath = dirpath + "precision"+xy+".csv"
    with open(filepath, "w", encoding="utf-8")  as f:
        xList = sorted(list(output.keys()))
        yList = sorted(list(output[xList[0]].keys()))
        led_x = ","+",".join([str(x) for x in xList])
        f.write(led_x+"\n")
        for allY in yList:
            f.write(str(allY) + ",")
            for allX in xList:
                pList = output[allX][allY]["p"]
                print(pList)
                if len(pList) == 0:
                    f.write("0,")
                else:
                    f.write(str(sum(pList)/len(pList))+",")
            f.write("\n")
    filepath = dirpath + "recall"+xy+".csv"
    with open(filepath, "w", encoding="utf-8")  as f:
        xList = sorted(list(output.keys()))
        yList = sorted(list(output[xList[0]].keys()))
        led_x = ","+",".join([str(x) for x in xList])
        f.write(led_x+"\n")
        for allY in yList:
            f.write(str(allY) + ",")
            for allX in xList:
                pList = output[allX][allY]["r"]
                if len(pList) == 0:
                    f.write("0,")
                else:
                    f.write(str(sum(pList)/len(pList))+",")
            f.write("\n")
    filepath = dirpath + "F_score"+xy+".csv"
    with open(filepath, "w", encoding="utf-8")  as f:
        xList = sorted(list(output.keys()))
        yList = sorted(list(output[xList[0]].keys()))
        led_x = ","+",".join([str(x) for x in xList])
        f.write(led_x+"\n")
        for allY in yList:
            f.write(str(allY) + ",")
            for allX in xList:
                pList = output[allX][allY]["F"]
                if len(pList) == 0:
                    f.write("0,")
                else:
                    f.write(str(sum(pList)/len(pList))+",")
            f.write("\n")

if __name__ == "__main__":
    for y in range(3):
        for x in range(y):
            execute(x, y)
