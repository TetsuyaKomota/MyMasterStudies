#-*- coding: utf-8 -*-

import DPM.ViewPointEncoder as encoder
import glob
import dill
import numpy as np
import itertools
import matplotlib.pyplot as plt
import os
from operator import itemgetter
import copy
import random

# Encoder 使って色々するやつ

objList = ["hand", "red", "blue", "green", "yellow"]

# 指定したファイル群から，指定した観点で状態を取得する
def getStateswithViewPoint(filepathList, baseList, refList, detail=False):
    output = {}
    for fpath in filepathList:
        if fpath[-4:] != ".csv":
            if detail==True:
                text = "[ViewPointManager]getSateswithViewPoint:"
                print(text + fpath + " is not csv file")
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
#   baseList    : 基準点
#   refList     : 参照点
#   movedObject : 移動した物体，事前にgetMovedObject で推定する
def getDistribution(stateDict, baseList, refList, movedObject):
    # データの数を取得しておく
    size = len(stateDict["before"])
    # 前後のデータ数が違えばそこでエラー終了
    if size != len(stateDict["after"]):
        print("[ViewPointManager]getDistribution:different size")
        return []
    # ゼロ個だったら何かおかしいのでエラー終了
    if size == 0:
        print("[ViewPointManager]getDistribution:size is zero")
        return []
    move = []
    transafter = []
    for i in range(size):
        transafter.append( \
            encoder.transformforViewPoint( \
                stateDict["after"][i], baseList, refList \
            ) \
        )
    # 選択した物体の最終位置のブレをスコアとして返す
    # 観点変換はここで使う
    diffDict = {}
    for o in movedObject:
        diffDict[o] = []
    for i in range(size):
        for s in movedObject:
            diffDict[s].append(np.array(transafter[i][s]))
    meanDict = {}
    for s in movedObject:
        meanDict[s] = sum(diffDict[s])/size
    
    diff = 0
    for i in range(size):
        for s in movedObject:
            diff += np.linalg.norm(np.array(transafter[i][s])-meanDict[s])
    return [meanDict, diff]

# 状態集合の前後の組から，移動物体を推定する
def getMovedObject(stateDict, detail=False):
    moveDict = {}
    for o in objList:
        moveDict[o] = 0
    for i in range(len(stateDict["before"])):
        for o in objList:
            bef = np.array(stateDict["before"][i][o])
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
    if detail == True:
        print("selected:" + str(selected))
    return selected
 
# 状態集合(未エンコード)の前後の組から，観点を推定する
#   stateDict = {"before":[前状態], "after":[後状態]}
#   before, after はインデックスで紐づけられている
def getViewPoint(stateDict, detail=False):
    # データの数を取得しておく
    size = len(stateDict["before"])
    # 前後のデータ数が違えばそこでエラー終了
    if size != len(stateDict["after"]):
        print("[ViewPointManager]getViewPoint:different size")
        return []
    output = []
    tempmin = 123456789

    # 移動物体を取得する
    # 移動物体は stateDict が一定な限り一定なはず
    moved = getMovedObject(stateDict)

    # 試すパターンはとりあえず，
    # baseList 物体3つまで，refList 1つまで
    # baseList はゼロ(原点基準)を許さないようにする
    for nb in range(3 +1):
        baseList = itertools.combinations(objList, nb)
        for b in baseList:
            # 移動物体を基準点に含む組み合わせは無視
            if len(set(moved)&set(b)) != 0:
                continue
            for nr in range(1 + 1):
                refList = itertools.combinations(objList, nr)
                for r in refList:
                    if detail == True:
                        print("test => " + str(b) + ":" + str(r))
                    # 基準点と参照点に重複がある場合は飛ばす
                    if len(set(b) & set(r)) != 0:
                        continue
                    score = getDistribution(stateDict, b, r, moved)
                    if tempmin == 123456789 or score[1] < tempmin:
                        better = {}
                        better["base"]  = b
                        better["ref"]   = r
                        better["score"] = score[1]
                        better["mean"]  = score[0]
                        output = [better] + output
                        tempmin = score[1]
    # 最高の結果のみ返す
    return output[0]

# 前後組を引数に，サンプリング->vp 学習を繰り返して
# 観点を多数決で推定する

def getViewPointwithSampling(stateDict, sampleSize=0.5, n_iter=50):
    # 組数を取得
    size = list(range(len(stateDict["before"])))
    # 観点数え上げ用の辞書
    vpdict = {}
    for _ in range(n_iter):
        # stateDict から半分のサンプリング
        # とりあえず一つのデータは一回まで
        # → 重複サンプルありにしてみる
        pick = {"before":[], "after":[], "fname":[]}
        random.shuffle(size)
        """
        for i in size[:int(len(size)*sampleSize)]:
            pick["before"].append(stateDict["before"][i])
            pick["after" ].append(stateDict["after" ][i])
            pick["fname" ].append(stateDict["fname" ][i])
        """
        for _ in range(int(len(size)*sampleSize)):
            idx = random.choice(size)
            pick["before"].append(stateDict["before"][idx])
            pick["after" ].append(stateDict["after" ][idx])
            pick["fname" ].append(stateDict["fname" ][idx])

        # サンプリング結果で vp 学習
        vp  = getViewPoint(pick)
        key = (vp["base"], vp["ref"])

        # サンプリング結果を vpdict に保存する
        # 分散の逆数を追加することで，高精度の観点に重みづけできる
        if key in vpdict.keys():
            vpdict[key] += 1.0/vp["score"]
        else:
            vpdict[key] =  1.0/vp["score"]

    # 多数決で最大の観点を取得
    points = sorted(vpdict.items(), key=lambda x: x[1])[0][0]
    
    # この観点を用いた場合の分布を求める
    moved = getMovedObject(stateDict)
    distribution = getDistribution(stateDict, points[0], points[1], moved)
    
    # getViewPoint と同じ形の返り値にして返す
    better = {}
    better["base"]  = points[0]
    better["ref"]   = points[1]
    better["score"] = distribution[1]
    better["mean"]  = distribution[0]
    return better

# getViewPoint の結果をもとに，次の状態を推定する
# state     : 状態
# viewPoint : getViewPoint の結果
def predictwithViewPoint(state, viewPoint):
    moved  = copy.deepcopy(state)
    base   = viewPoint["base"] 
    ref    = viewPoint["ref" ] 
    mean   = viewPoint["mean"] 
    for m in mean:
        moved[m] = viewPoint["mean"][m]
    moved = encoder.retransformforViewPoint(moved, base, ref)
    output = {}
    for s in state:
        if s in mean:
            output[s] = moved[s]
        else:
            output[s] = state[s]
    return output 

# 状態を引数に，描画する
# 変換前の 軸の向きも一緒に描画する
def show(state, title="show", xlim=(-5000, 5000), ylim=(-5000, 5000)):
    for st in state:
        color = ""
        if st == "hand":
            color = "black"
        elif st in objList:
            color = st
        else:
            continue
        plt.scatter(state[st][0], state[st][1], c=color, s=120)
    plt.title(title)
    plt.xlim(xlim[0], xlim[1])
    plt.ylim(ylim[0], ylim[1])
    plt.show()
    return True

# 状態二つを引数に，差を計算する
def calcDifference(state1, state2, objs=objList):
    error = 0
    for o in objs:
        error += np.linalg.norm(state1[o]-state2[o])
    return error 

# 状態とパスとファイル名を引数に，画像書き出し
def savefig(state,path="tmp/forslides",name="fig.png",log=True,inter=False):
    if log == False:
        plt.clf()
    # TODO 後で消す
    plt.xlim(-5000, 5000)
    plt.ylim(-5000, 5000)
    for st in state:
        color = ""
        if st == "hand":
            color = "black"
        elif st in objList:
            color = st
        else:
            continue
        scale = 120
        m     = "o"
        if inter == True and st == "hand":
            scale *= 4
            m      = "*"
            color  = "gray"
        plt.scatter(state[st][0], state[st][1], marker=m, c=color, s=scale)
    plt.title("savefig")
    saveas = path
    if saveas[-1] != "/":
        saveas += "/"
    saveas += name
    plt.savefig(saveas)
    # plt.close()
    return True

if __name__ == "__main__":
    filepaths = glob.glob("tmp/log_MakerMain/*")
    # データ取得
    datas = getStateswithViewPoint(filepaths, [], [])
    # 0 番と 100 番のデータのみを取り出してみる
    stateDict = {}
    stateDict["before"] = []
    stateDict["after"]  = []
    for d in datas:
        stateDict["before"].append(datas[d][0])
        stateDict["after" ].append(datas[d][99])
    # 学習
    res = getViewPoint(stateDict)
    print("result:")
    print("score:" + str(res["score"]) + "\t\t")
    print("base:"  + str(res["base"])  + "\t\t")
    print("ref:"   + str(res["ref"])   + "\t\t")
    print("mean:"  + str(res["mean"])  + "\t\t")
    # 推定
    for i in range(10):
        test = datas["log00000000" + str(i) +".csv"][0]
        show(test, title="before")
        truth= datas["log00000000" + str(i) +".csv"][99]
        show(truth,title="truth")
        test = predictwithViewPoint(test, res)
        show(test, title="after")

