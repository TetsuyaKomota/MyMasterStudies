# coding = utf-8

# とりあえずデータを見てみよう
# 自爆テロを時系列順に並べて，発生場所を HMM で予測してみよう

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


if __name__ == "__main__":
    print(readCSV("tmp/data.csv"))
