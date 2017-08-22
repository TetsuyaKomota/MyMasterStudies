#-*- coding: utf-8 -*-

import ViewPointEncoder as encoder
import glob
import dill
import numpy as np

# Encoder 使って色々するやつ

# 指定したファイル群から，指定した観点で状態を取得する
def getStateswithViewPoint(filepathList, baseList, refList):
    output = {}
    for fname in filepathList:
        output[fname] = []
        with open(fname, "r", encoding="utf-8") as f:
            while True:
                line = f.readline()
                if line == "":
                    break
                bstate = encoder.encodeState(line)
                astate = encoder.translateforViewPoint(bstate,baseList,refList)
                data   = encoder.serialize(astate)
                output[fname].append(data)
    return output

# 状態集合(エンコード，観点変換済み)の前後の組から，平均と偏差を求める
# 偏差はユークリッド距離の平均とのずれの平均とする
#   stateDict = {"before":[前状態], "after":[後状態]}
def getDistribution(stateDict):
    move = []
    for i in range(len(stateDict["before"])):
        nb = np.array(stateDict["before"][i])
        na = np.array(stateDict["after"][i])
        move.append(na-nb)
    mean = sum(move)/len(move)
    
    diff = 0
    for m in move:
        diff += np.linalg.norm(m-mean)
    return [mean, diff]


if __name__ == "__main__":
    filepaths = glob.glob("tmp/log_MakerMain/GettingIntermediated/*")
    datas = getStateswithViewPoint(filepaths, ["hand"], [])
    print(datas)
    with open("tmp/log_MakerMain/dills/test_pov.dill", "wb") as f:
        dill.dump(datas, f)
