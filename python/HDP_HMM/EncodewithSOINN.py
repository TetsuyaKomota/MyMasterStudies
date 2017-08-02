from SOINN.SOINN_for_python import SOINN
import glob
import dill

step = 5

# soinn = SOINN(step * 2, 99999999999999999, 99999999999999999)
soinn = SOINN(step * 2, 10000, 10000, n_iter=1, noise_var=0, detail=True)

X = []


filenames = glob.glob("tmp/log_MakerMain/PostProcessed/*")
fnameList = [] # dill する辞書のキーに使うファイル名
for fname in filenames:
    if fname[-4:] != ".csv":
        continue
    fnameList.append(fname[-12:-4])
    temp = []
    for i in range(step):
        temp.append([0.0, 0.0])
    with open(fname, "r", encoding="utf-8") as f:
        while True:
            line = f.readline().split(",")
            if len(line) < 2:
                break
            temp = temp[1:]
            temp.append([float(line[0]), float(line[1])])
            x = []
            for t in temp:
                x.append(t[0])
                x.append(t[1])
            X.append(x)
for d in X:
    print(d)
soinn.fit(X)
print(soinn.getClassNum())

output = {}
for fname in filenames:
    if fname[-4:] != ".csv":
        continue
    Z = []
    temp = []
    for i in range(step):
        temp.append([0.0, 0.0])
    with open(fname, "r", encoding="utf-8") as f:
        while True:
            line = f.readline().split(",")
            if len(line) < 2:
                break
            temp = temp[1:]
            temp.append([float(line[0]), float(line[1])])
            x = []
            for t in temp:
                x.append(t[0])
                x.append(t[1])
            Z.append(x)
    output[fname[-16:-4]] = soinn.classifier(Z)

# 学習したモデルをもとに，推定を行う
# dill 出力して，それをHPYLM で参照する

results       = {}
results_naive = {}
for i, d in enumerate(output):
    result       = []
    result_naive = []
    pre = d
    for p in pre:
        result_naive.append(p)
        if len(result) == 0 or p != result[-1]:
            result.append(p)
    results[fnameList[i]]       = result
    results_naive[fnameList[i]] = result_naive
with open("tmp/log_MakerMain/dills/SOINN_results.dill", "wb")  as f:
    dill.dump(results, f)
    print("Successfully dumping : results")
with open("tmp/log_MakerMain/dills/SOINN_results_naive.dill", "wb")  as f:
    dill.dump(results_naive, f)
    print("Successfully dumping : results_naive")

