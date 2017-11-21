from SOINN.SOINN_for_python import SOINN
import glob
import dill
import os

def execute(step = 3, soinnN = 5000, soinnE = 5000, dillpath = ""):
    params = "_".join([str(step), str(soinnN), str(soinnE)])
    # もしそのパラメータで以前学習済みなら，学習済みのモデルを使う
    if os.path.exists("tmp/log_MakerMain/dills/SOINN_results_" + params + ".dill"):
        with open("tmp/log_MakerMain/dills/SOINN_results_" + params + ".dill", "rb")  as f:
            results = dill.load(f)
        with open("tmp/log_MakerMain/dills/SOINN_results_" + params + "_naive.dill", "rb")  as f:
            results_naive = dill.load(f)
        with open("tmp/log_MakerMain/dills/SOINN_results" + dillpath + ".dill", "wb")  as f:
            dill.dump(results, f)
            print("Successfully dumping : results")
        with open("tmp/log_MakerMain/dills/SOINN_results" + dillpath + "_naive.dill", "wb")  as f:
            dill.dump(results_naive, f)
            print("Successfully dumping : results_naive")
        return
       
    # step = 3

    # soinn = SOINN(step * 2, 99999999999999999, 99999999999999999)
    # soinn = SOINN(step * 2, 1000000, 1000000, n_iter=1, noise_var=0, detail=True)
    soinn = SOINN(step * 2, soinnN, soinnE, n_iter=1, noise_var=0)

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
    for d in range(5):
        print(X[d])

    print("input for SOINN:" + str(len(X)))   
 
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
        output[fname[-18:-4]] = soinn.classifier(Z)

    # 学習したモデルをもとに，推定を行う
    # dill 出力して，それをHPYLM で参照する

    results       = {}
    results_naive = {}
    for d in output:
        result       = []
        result_naive = []
        pre = output[d]
        for p in pre:
            result_naive.append(p)
            if len(result) == 0 or p != result[-1]:
                result.append(p)
        results[d]       = result
        results_naive[d] = result_naive
    with open("tmp/log_MakerMain/dills/SOINN_results" + dillpath + ".dill", "wb")  as f:
        dill.dump(results, f)
        print("Successfully dumping : results")
    with open("tmp/log_MakerMain/dills/SOINN_results" + dillpath + "_naive.dill", "wb")  as f:
        dill.dump(results_naive, f)
        print("Successfully dumping : results_naive")

    # パラメータごとにセーブしておく
    with open("tmp/log_MakerMain/dills/SOINN_results_" + params + ".dill", "wb")  as f:
        dill.dump(results, f)
    with open("tmp/log_MakerMain/dills/SOINN_results_" + params + "_naive.dill", "wb")  as f:
        dill.dump(results_naive, f)



if __name__ == "__main__":
    execute()
