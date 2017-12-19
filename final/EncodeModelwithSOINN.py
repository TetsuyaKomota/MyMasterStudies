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

from SOINN.SOINN_for_python import SOINN
import dill
import os
import glob

step = 3
soinnN = 2500
soinnE = 2500

def fit():
    filepaths = glob.glob("tmp/log/*.csv")
    
    X = []
    for filepath in filepaths:
        # step ステップ幅を切り出す
        dummy = len(X)
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

    # SOINN を学習
    soinn = SOINN(step * 2, soinnN, soinnE, n_iter=1, noise_var=0)
    soinn.fit(X)
    if os.path.exists("tmp/dills") == False:
        os.mkdir("tmp/dills")
    with open("tmp/dills/soinn.dill", "wb") as f:
        dill.dump(soinn, f)

    return soinn

def predict():
    if os.path.exists("tmp/dills/soinn.dill") == True:
        with open("tmp/dills/soinn.dill", "rb") as f:
            soinn = dill.load(f)
    else:
        soinn = fit()

    output = {}
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

        # 推定
        output[os.path.basename(filepath)[:-4]] = soinn.classifier(Z)

    with open("tmp/dills/encoded.dill", "wb") as f:
        dill.dump(output, f)

    return output

if __name__ == "__main__":
    predict()
