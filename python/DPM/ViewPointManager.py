#-*- coding: utf-8 -*-

import ViewPointEncoder as encoder
import glob
import dill
import numpy as np
import itertools
import matplotlib.pyplot as plt
import os
from operator import itemgetter

# Encoder 使って色々するやつ

# 指定したファイル群から，指定した観点で状態を取得する
def getStateswithViewPoint(filepathList, baseList, refList):
    output = {}
    for fpath in filepathList:
        if fpath[-4:] != ".csv":
            print(fpath + " : not csv file")
            continue
        # パスをキーにして管理すると面倒なのでファイル名に変更
        filename = os.path.basename(fpath)
        # print("file:"+filename)
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

# 状態集合の前後の組，基準と参照点から，平均と偏差を求める
# 偏差はユークリッド距離の平均とのずれの平均とする
#   stateDict = {"before":[前状態], "after":[後状態]}
#   baseList : 基準点
#   refList  : 参照点
def getDistribution(stateDict, baseList, refList):
    # データの数を取得しておく
    size = len(stateDict["before"])
    # 前後のデータ数が違えばそこでエラー終了
    if size != len(stateDict["after"]):
        print("[ViewPointManager]getViewPoint:different size")
        return []
    # ゼロ個だったら何かおかしいのでエラー終了
    if size == 0:
        print("[ViewPointManager]getViewPoint:size is zero")
        return []
    move = []
    """
    # 観点変換する
    trans = {}
    trans["before"] = []
    trans["after"]  = []
    for i in range(size):
        trans["before"].append(encoder.transformforViewPoint(stateDict["before"][i], baseList, refList))
        trans["after"].append(encoder.transformforViewPoint(stateDict["after"][i], baseList, refList))
    """
    transafter = []
    for i in range(size):
        transafter.append(encoder.transformforViewPoint(stateDict["after"][i], baseList, refList))
    # 評価対象は「最も大きく動いている物体」に限定
    # 各物体の「前後で動いた量」の合計を求める
    objList = ["hand", "red", "blue", "green", "yellow"]
    moveDict = {}
    for o in objList:
        moveDict[o] = 0
    for i in range(size):
        for o in objList:
            # bef = np.array(trans["before"][i][o])
            bef = np.array(stateDict["before"][i][o])
            # aft = np.array(trans["after"][i][o])
            aft = np.array(stateDict["after"][i][o])
            moveDict[o] += np.linalg.norm(aft-bef)
    # 寄与率が一定以上になるまで物体を選択する
    rate = 0.75
    tempdiff = 0
    # moveDict を降順ソート
    moveList = sorted(moveDict.items(), key=itemgetter(1), reverse=True)
    selected = []
    for m in moveList:
        selected.append(m[0])
        tempdiff += m[1]
        if tempdiff >= sum(moveDict.values()) * rate:
            break
    # print("moveList:" + str(moveList))
    print("selected:" + str(selected))
    # 選択した物体の最終位置のブレをスコアとして返す
    # 観点変換はここで使う
    diffDict = {}
    for o in selected:
        diffDict[o] = []
    for i in range(size):
        for s in selected:
            # diffDict[s].append(np.array(trans["after"][i][s]))
            diffDict[s].append(np.array(transafter[i][s]))
    meanDict = {}
    for s in selected:
        meanDict[s] = sum(diffDict[s])/size
    
    diff = 0
    for i in range(size):
        for s in selected:
            # diff += np.linalg.norm(np.array(trans["after"][i][s])-meanDict[s])
            diff += np.linalg.norm(np.array(transafter[i][s])-meanDict[s])
    return [selected, diff]
    """
    for i in range(size):
        nb = np.array(encoder.serialize(trans["before"][i]))
        na = np.array(encoder.serialize(trans["after"][i]))
        move.append(na-nb)
    mean = sum(move)/len(move)
    
    diff = 0
    for m in move:
        diff += np.linalg.norm(m-mean)
    return [mean, diff]
    """

# 状態集合(未エンコード)の前後の組から，観点を推定する
#   stateDict = {"before":[前状態], "after":[後状態]}
#   before, after はインデックスで紐づけられている
def getViewPoint(stateDict):
    # データの数を取得しておく
    size = len(stateDict["before"])
    # 前後のデータ数が違えばそこでエラー終了
    if size != len(stateDict["after"]):
        print("[ViewPointManager]getViewPoint:different size")
        return []
    output = []
    tempmin = 10000000000000
    objList = ["hand", "red", "blue", "green", "yellow"]
    # 試すパターンはとりあえず，
    # baseList 物体3つまで，refList 1つまで
    for nb in range(3 +1):
        baseList = itertools.combinations(objList, nb)
        for b in baseList:
            for nr in range(1 + 1):
                refList = itertools.combinations(objList, nr)
                for r in refList:
                    print("test => " + str(b) + ":" + str(r))
                    # 基準点と参照点に重複がある場合は飛ばす
                    if len(set(b) & set(r)) != 0:
                        continue
                    score = getDistribution(stateDict, b, r)
                    if score[1] < tempmin:
                        output = [{"base":b, "ref":r, "score":score[1]}] + output
                        tempmin = score[1]
    return output

# 状態を引数に，描画する
# 返還前の 軸の向きも一緒に描画する
def show(state, title="show"):
    for st in state:
        color = ""
        if st == "hand":
            color = "black"
        elif st in ["red", "blue", "green", "yellow"]:
            color = st
        else:
            continue
        plt.scatter(state[st][0], state[st][1], c=color, s=120)
    plt.title(title)
    plt.show()
    return True

if __name__ == "__main__":
    """
    filepaths = glob.glob("tmp/log_MakerMain/GettingIntermediated/3-2500-2500-9/*")
    # hand を中心に変換したデータを取得
    datas = getStateswithViewPoint(filepaths, ["hand"], [])
    for d in datas:
        print(d)
        print(datas[d])
    with open("tmp/log_MakerMain/dills/test_pov.dill", "wb") as f:
        dill.dump(datas, f)
    print("\n\n\n")
    testData = datas[list(datas.keys())[0]]
    # 描画のテスト
    print(testData[0])
    show(testData[0])
    # 観点取得のテスト
    getViewPoint(testData)
    """
    filepaths = glob.glob("tmp/log_MakerMain/*")
    # hand を中心に変換したデータを取得
    # datas = getStateswithViewPoint(filepaths, ["hand"], [])
    # データ取得
    datas = getStateswithViewPoint(filepaths, [], [])
    """
    # 動きを見てみる
    for i, d in enumerate(datas["log000000001.csv"]):
        if i < 450:
            continue
        if i % 1 == 0:
            show(d, title=str(i))
    """
    # 0 番と 100 番のデータのみを取り出してみる
    stateDict = {}
    stateDict["before"] = []
    stateDict["after"]  = []
    for d in datas:
        stateDict["before"].append(datas[d][0])
        stateDict["after"].append(datas[d][100])
    show(stateDict["before"][0])
    show(stateDict["after"][0])
    # 推定
    res = getViewPoint(stateDict)
    print("result:")
    for r in res:
        print("score:" + str(r["score"]) + "\t\tbase:"+str(r["base"])+"\t\tref:"+str(r["ref"]))
