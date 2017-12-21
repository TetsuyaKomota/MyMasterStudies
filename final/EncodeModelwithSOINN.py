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
from SOINN.FastSOINN import SOINN
import numpy as np
import dill
import os
import glob
import sys

step = 5
soinnN = 5000000
soinnE = 100

def fit():
    if os.path.exists("tmp/dills") == False:
        os.mkdir("tmp/dills")
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
            soinn.saveModel(path="tmp/dills/")

    return soinn

def predict():
    if os.path.exists("tmp/dills/soinn.dill") == True:
        soinn = SOINN(step * 2, soinnN, soinnE)
        soinn.loadModel(path="tmp/dills/")
    else:
        soinn = fit()

    output = {}
    filepaths = glob.glob("tmp/log/*.csv")
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

    with open("tmp/dills/encoded.dill", "wb") as f:
        dill.dump(output, f)

    return output

if __name__ == "__main__":
    # dill.dump の再帰し過ぎで怒られるので設定
    # sys.setrecursionlimit(10000)
    predict()