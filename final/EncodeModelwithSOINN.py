# coding = utf-8

# やること
# 動作データ → 符号列

# メソッド
# ・学習
#   tmp/log にあるデータを全部 SOINN に代入
#   できた SOINN を dill.dump
#
# ・符号化
#   tmp/dills/soinn.dill をロード
#   tmp/log にあるデータを全部符号化
#   できた符号列を，ファイル名キーの dict にする
#   それを dill.dump

# from SOINN.SOINN_for_python import SOINN
from models.FastSOINN import SOINN
import numpy as np
import dill
import os
import glob
import sys

def fit(dillpath, step, soinnN, soinnE):
    if os.path.exists("tmp/dills/") == False:
        os.mkdir("tmp/dills/")
    if os.path.exists("tmp/dills/"+dillpath) == False:
        os.mkdir("tmp/dills/"+dillpath)
    filepaths = glob.glob("tmp/log/*.csv")
    # soinn = SOINN(step * 2, soinnN, soinnE, n_iter=1, noise_var=0)
    soinn = SOINN(step * 2, soinnN, soinnE)

    for i, filepath in enumerate(filepaths):
        print("[EncodeModel] input : " + os.path.basename(filepath))
        print("[EncodeModel] current class num : " + str(soinn.classifier()))
        # step ステップ幅を切り出す
        X = []
        X.append([0 for _ in range(step*2)])
        with open(filepath, "r", encoding="utf-8") as f:
            while True:
                line = f.readline()
                if line == "":
                    break
                # hand の速度成分の部分だけ取り出す
                # str なので float にキャスト
                pos = [float(p) for p in line.split(",")[3:5]]
                # temp を更新
                X.append(X[-1][2:] + pos)
        
        # X[0] はダミーなので消しておく
        X.pop(0)

        # np.array に変換
        X = [np.array(x) for x in X]

        # SOINN を学習
        soinn.fit(X)
        
        if i%200==0:
            soinn.saveModel(path="tmp/dills/"+dillpath)

    return soinn

def predict(dillpath, logpath, step, soinnN, soinnE):
    if os.path.exists("tmp/dills/"+dillpath+"soinn.dill") == True:
        soinn = SOINN(step * 2, soinnN, soinnE)
        soinn.loadModel(path="tmp/dills/"+dillpath)
        soinn.removeUnnecessaryNode()
        soinn.classifier()
        # soinn.prunning()
    else:
        soinn = fit(dillpath, step, soinnN, soinnE)

    output = {}
    filepaths = glob.glob(logpath + "*.csv")
    for filepath in filepaths:
        # step ステップ幅を切り出す
        Z = []
        Z.append([0 for _ in range(step*2)])
        with open(filepath, "r", encoding="utf-8") as f:
            while True:
                line = f.readline()
                if line == "":
                    break
                # hand の速度成分の部分だけ取り出す
                # str なので float にキャスト
                pos = [float(p) for p in line.split(",")[3:5]]
                # temp を更新
                Z.append(Z[-1][2:]+pos)
        
        # Z[0] はダミーなので消しておく
        Z.pop(0)

        # np.array に変換
        Z = [np.array(z) for z in Z]

        # 推定
        output[os.path.basename(filepath)[:-4]] = soinn.predict(Z)

    if "test" in logpath:
        with open("tmp/dills/"+dillpath+"encoded_test.dill", "wb") as f:
            dill.dump(output, f)
    else:
        with open("tmp/dills/"+dillpath+"encoded.dill", "wb") as f:
            dill.dump(output, f)

    return output

if __name__ == "__main__":
    """
    # train データによる学習と推定
    # train データも推定するのは NPYLM の学習に使うため
    predict("", "tmp/log/", 5, 5000000, 100)

    # test データによる推定
    predict("", "tmp/log_test/", 5, 5000000, 100)
    """
    for N in [3000, 5000000]:
        for E in [100, 3000, 5000000]:
            predict("SOINN_N="+str(N)+",E="+str(E)+"/", "tmp/log/",5,N,E)
            predict("SOINN_N="+str(N)+",E="+str(E)+"/", "tmp/log_test/",5,N,E)
