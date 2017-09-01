#-*- coding: utf-8 -*-

import ViewPointEncoder as encoder
import glob
import dill
import numpy as np
import itertools
import matplotlib.pyplot as plt
import os

# Encoder 使って色々するやつ

# 指定したファイル群から，指定した観点で状態を取得する
def getStateswithViewPoint(filepathList, baseList, refList):
    output = {}
    for fpath in filepathList:
        # パスをキーにして管理すると面倒なのでファイル名に変更
        filename = os.path.basename(fpath)
        output[filename] = []
        with open(fpath, "r", encoding="utf-8") as f:
            while True:
                line = f.readline()
                if line == "":
                    break
                bstate = encoder.encodeState(line)
                astate = encoder.transformforViewPoint(bstate,baseList,refList)
                # data   = encoder.serialize(astate)
                data = astate
                output[filename].append(data)
    return output

# 状態集合(エンコード，観点変換済み)の前後の組から，平均と偏差を求める
# 偏差はユークリッド距離の平均とのずれの平均とする
#   stateDict = {"before":[前状態], "after":[後状態]}
def getDistribution(stateDict):
    move = []
    for i in range(len(stateDict["before"])):
        nb = np.array(encoder.serialize(stateDict["before"][i]))
        na = np.array(encoder.serialize(stateDict["after"][i]))
        move.append(na-nb)
    mean = sum(move)/len(move)
    
    diff = 0
    for m in move:
        diff += np.linalg.norm(m-mean)
    return [mean, diff]

# 状態集合(未エンコード)の前後の組から，観点を推定する
#   stateDict = {"before":[前状態], "after":[後状態]}
#   before, after はインデックスで紐づけられている
def getViewPoint(stateDict):
    output = []
    tempmin = 100000
    objList = ["hand", "red", "blue", "green", "yellow"]
    # 試すパターンはとりあえず，
    # baseList 物体3つまで，refList 1つまで
    for n in range(3 +1):
        baseList = itertools.combinations(ojbList, n)
        for b in baseList:
            for nr in range(1 + 1):
                print("")
    return output

# 状態を引数に，描画する
# 返還前の 軸の向きも一緒に描画する
def show(state):
    for st in state:
        color = ""
        if st == "hand":
            color = "black"
        elif st in ["red", "blue", "green", "yellow"]:
            color = st
        else:
            continue
        plt.scatter(state[st][0], state[st][1], c=color, s=120)
    plt.show()
    return True

if __name__ == "__main__":
    filepaths = glob.glob("tmp/log_MakerMain/GettingIntermediated/3-2500-2500-9/*")
    datas = getStateswithViewPoint(filepaths, ["hand"], [])
    for d in datas:
        print(d)
        print(datas[d])
    with open("tmp/log_MakerMain/dills/test_pov.dill", "wb") as f:
        dill.dump(datas, f)
    print("\n\n\n")
    print(datas[list(datas.keys())[0]][0])
    show(datas[list(datas.keys())[0]][0])
