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
import dill
import numpy as np
from functools import reduce
import matplotlib.pyplot as plt

def visualize():
    with open("tmp/dills/parsed.dill", "rb") as f:
        parsed = dill.load(f)

    bag = []
    for filename in parsed.keys():
        bag += parsed[filename]

    plt.hist(bag, bins=max(bag)+1)
    plt.show()

def evaluate(resultName="result", dirname="", mode="a"):
    visualize()
    with open("tmp/dills/" + dirname + "parsed.dill", "rb") as f:
        parsed = dill.load(f)
   
    # precision : 境界と推定したもののうち，正解の割合
    # recall    : 正解のうち，境界と推定したものの割合
    # ↓
    # precision は単純に100n+l 内の境界の数を数え，推定境界全体数 で割る
    # recall は上記の数を，データ数×正解の境界数 で割る
    # どちらにしても，正解の境界の数え方に注意
    # 一つの 100n に対し．一つまでしか計上しない

    succDict  = {}
    numofSucc = 4
    e         = 10 # 許容ステップ誤差
    for filename in parsed.keys():
            succDict[filename] = 0
            for n in range(1, numofSucc+1):
                temp = [np.abs(step-100*n)<e for step in parsed[filename]]
                temp = reduce(lambda x, y : x or y, temp)
                succDict[filename] += int(temp)
    succ      = sum(succDict.values())
    precision = succ / sum([len(sList) for sList in parsed.values()])
    recall    = succ / (len(parsed.keys()) * numofSucc)
    if precision + recall == 0:
        fScore = 0
    else:
        fScore = 2.0/(1.0/precision + 1.0/recall)
    # csv 書き出し
    dirpath = "tmp/results/"
    
    if os.path.exists(dirpath) == False:
        os.mkdir(dirpath)
    with open(dirpath+"results_NPYLM.csv", mode, encoding="utf-8") as f:
        if mode == "w":
            f.write("resultname,precision,recall,f_score\n")
        text  = str(resultName) + ","
        text += str(precision)  + ","
        text += str(recall)     + ","
        text += str(fScore)     + "\n"
        f.write(text)

    print("%4f, %4f, %4f" % (precision, recall, fScore))

if __name__ == "__main__":
    evaluate()
