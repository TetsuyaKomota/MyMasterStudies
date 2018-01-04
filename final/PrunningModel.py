# coding = utf-8

# やること
# 単語列 → 境界列

# メソッド
# ・剪定
#   tmp/dills/parsed.dill をロード
#   tmp/log のデータと照らし合わせ，直前の状態と
#   hand 以外に変化がない境界は削除
#   剪定し終わった境界列は状態列に

import os
import dill
import glob
import numpy as np
from functools import reduce

threshold = 10

def prunning(dillpath):
    with open("tmp/dills/"+dillpath+"parsed_test.dill", "rb") as f:
        parsed = dill.load(f)

    output = {}

    for filename in parsed.keys():
        # ログファイルをロード
        logList = []
        logpath = "tmp/log/" + filename + ".csv"
        with open(logpath, "r", encoding="utf-8") as f:
            while True:
                line = f.readline().split(",")
                if len(line) < 2:
                    break
                # [0:5] は step と hand の位置と速度なので無視
                logList.append([float(l) for l in line[5:-1]])

        # 有意な境界のみ取得
        output[filename] = []
        for step in parsed[filename]:
            # 最初の一つは無条件で入れる
            if len(output[filename]) == 0:
                output[filename].append(step)
                continue
            
            # 直前のステップとの状態を比較する
            bList = np.array(logList[output[filename][-1]])
            aList = np.array(logList[step])
           
            # (b-a)^2 > Thresh (変化したか) の OR 畳み込み
            # → 一つも変化してないときのみ False になる
            flag = reduce(lambda x,y:x or y, list((aList-bList)**2 > 10))

            if flag == True:
                output[filename].append(step)

    with open("tmp/dills/"+dillpath+"prunned.dill", "wb") as f:
        dill.dump(output, f)

    return output

if __name__ == "__main__":
    # prunning("CHEAT/")
    filepaths = glob.glob("tmp/dills/*")
    for filepath in filepaths:
        if os.path.isdir(filepath) == False:
            continue
        if os.path.exists(filepath + "/parsed_test.dill") == True:
            dirname = os.path.basename(filepath)
            prunning(dirname+"/")
