from SOINN.SOINN_for_python import SOINN
import glob
import dill

step = 5

soinn = SOINN(step * 2, 99999999999999999, 99999999999999999)

X = []


filenames = glob.glob("tmp/log_MakerMain/PostProcessed/*")
for fname in filenames:
    if fname[-4:] != ".csv":
        continue
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
print(soinn.getNodeNum())

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
            temp.append([float(line[1]), float(line[2])])
            x = []
            for t in temp:
                x.append(t[0])
                x.append(t[1])
            Z.append(x)
    output[fname[-16:-4]] = soinn.classifier(Z)

for o in output:
    print(o)
    print(output[o])
with open("tmp/log_MakerMain/dills/SOINN_results.dill", "wb") as f:
    dill.dump(output, f)
    print("Successfuly dumping SOINN_results.dill")
