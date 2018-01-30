# coding = utf-8

# やること
# parsed.dill をロードしてヒストグラム表示
# F 値も計算する(正解ステップを設定できるようにしよう)

# メソッド
# ・visualize
#   ヒストグラム出す
#
# ・evaluate
#   F値求める

import os
import glob
import dill
import numpy as np
from functools import reduce
import matplotlib.pyplot as plt

dirpath  = "tmp/results/"
dillname = "parsed.dill"
# dillname = "matching.dill"

def visualize(dirname="", isSaveImg=False):
    with open("tmp/dills/" + dirname + dillname, "rb") as f:
        parsed = dill.load(f)

    bag = []
    for filename in parsed.keys():
        bag += parsed[filename]

    plt.hist(bag, bins=max(bag)+1)
    if os.path.exists(dirpath) == False:
        os.mkdir(dirpath)
    if isSaveImg == True:
        if os.path.exists(dirpath + "img/") == False:
            os.mkdir(dirpath + "img/")
        imgname = "img_" + dillname.split(".")[0] + "_"
        plt.savefig(dirpath + "img/" + imgname + dirname[:-1] + ".jpg")
    # plt.show()
    plt.figure()

def evaluate(resultName="result", dirname="", mode="a", isSaveImg=False):
    visualize(dirname, isSaveImg)
    with open("tmp/dills/" + dirname + dillname, "rb") as f:
        parsed = dill.load(f)
   
    # precision : 境界と推定したもののうち，正解の割合
    # recall    : 正解のうち，境界と推定したものの割合
    # ↓
    # precision は単純に200n+l 内の境界の数を数え，推定境界全体数 で割る
    # recall は上記の数を，データ数×正解の境界数 で割る
    # どちらにしても，正解の境界の数え方に注意
    # 一つの 200n に対し．一つまでしか計上しない
    # 動作自体は 100 ステップずつだが．環境的に重要なのは 200, 400 なので，
    # 正解対象を 200n とする

    succDict  = {}
    # 700 モードなら 3, 500 モードなら 2
    numofSucc = 3
    # numofSucc = 2
    e         = 10 # 許容ステップ誤差
    for filename in parsed.keys():
            succDict[filename] = 0
            print("filename:" + str(filename) + ":" + str(parsed[filename]))
            for n in range(1, numofSucc+1):
                # temp = [np.abs(step-200*n)<e for step in parsed[filename]]
                # 例えば 200 に対して，299 までは正解とみなすべきで，
                # 299+e までを許容誤差とするべき
                # 最後の条件は「最終状態を正解としない」
                # 400 + 100+e を許容すると 499 は許容されるが
                # これは自明なので階としては無視
                temp = [step>200*n-e and (step-200*n)<100+e and step != 200*numofSucc+99 for step in parsed[filename]]
                print("step:" + str(200*n) + ":" + str(temp))
                temp = reduce(lambda x, y : x or y, temp)
                succDict[filename] += int(temp)
    succ      = sum(succDict.values())
    # precision の -2 は終始端を無視する為
    precision = succ / sum([len(sList)-2 for sList in parsed.values()])
    recall    = succ / (len(parsed.keys()) * numofSucc)
    if precision + recall == 0:
        fScore = 0
    else:
        fScore = 2.0/(1.0/precision + 1.0/recall)
    # csv 書き出し
    
    csvName = dillname.split(".")[0]
    filepath = dirpath + "results_" + csvName + ".csv"
    with open(filepath, mode, encoding="utf-8") as f:
        if mode == "w":
            f.write("resultname,precision,recall,f_score\n")
        text  = str(resultName) + ","
        text += str(precision)  + ","
        text += str(recall)     + ","
        text += str(fScore)     + "\n"
        f.write(text)

    print("%4f, %4f, %4f" % (precision, recall, fScore))

if __name__ == "__main__":
    # evaluate("CHEAT/", "CHEAT/", mode="w", isSaveImg=True)
    # exit()
    filepaths = glob.glob("tmp/dills/*")
    for filepath in filepaths:
        if os.path.isdir(filepath) == False:
            continue
        if os.path.exists(filepath + "/" + dillname) == True:
            dn = os.path.basename(filepath) + "/"
            evaluate(dn, dn, mode="a", isSaveImg=True)
