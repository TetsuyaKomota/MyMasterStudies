# coding = utf-8

import DPM.ViewPointManager as manager
import copy
import numpy as np
import glob
import dill 
import os
import re

THRESHOLD = 1.7

# 状態列と開始ステップと観点モデルを引数に，
# 追加で推定される途中状態に最も近い状態を返す
def getAdditionalIntermediate(stateList, step, viewPoint, detail=False):
    # 指定したステップ番号のデータを取得する
    print("[predictMatching]getAdditionalIntermediate:step:"+str(step))
    bState = stateList[step]
    # 取得したデータに対して次の状態を予測する
    aState = manager.predictwithViewPoint(bState, viewPoint)
    # 予測した状態に最も近い状態を stateList から推定する
    output = stateList[step]
    tempdiff = 1000000000
    for state in stateList:
        if state["step"] <= bState["step"]:
            continue
        curError = manager.calcDifference(state, aState)
        if detail == True:
            debugLine = "[DynamicalProgramming]getAdditionalIntermediate:"
            debugLine += "step:" + str(state["step"])
            debugLine += "\t\terror:" + str(curError) 
            print(debugLine)
        # もしtempdiff より小さくなったなら更新する
        if curError < tempdiff:
            tempdiff = curError
            output = state
        # もし tempdiff + RANGE 以上になったなら，
        # もうその先で更新の見込みはないとして終了する
        # elif curError >= tempdiff + 1500:
        elif curError >= 5*tempdiff:
            break
    return output

# ディレクトリ名を指定して，ファイル名をキー，境界のidx リストを値とする辞書を作る
def getInterDict(dirname):
    output = {}
    fpaths = glob.glob("tmp/log_MakerMain/GettingIntermediated/"+dirname+"/*")
    for fpath in fpaths:
        if os.path.isdir(fpath) == True:
            continue
        fname = os.path.basename(fpath)
        fname = re.sub("inter", "log", fname)
        output[fname] = []
        with open(fpath, "r", encoding="utf-8") as f:
            while True:
                line = f.readline()
                if line == "":
                    break
                # csv ファイルの境界のインデックスは 1~500 になっているので，
                # 0~499 にするために 1引く
                output[fname].append(int(line.split(",")[0])-1)
    return output

# 全データと境界列から，マッチング群を推定して返す
# interDict : dict : ファイル名をキーに，境界状態のステップ数のリストを持つ辞書
def DP_main_2(datas, interDict, sampleSize=0.5, n_iter=50, distError=0.005):
    output = {"matching":[], "pending":[]}
    rests = copy.deepcopy(interDict)
    # 境界が 0 番, 500番以外にないデータはここで除外する
    temprests = {}
    for r in rests:
        if len(rests[r]) > 2:
            temprests[r] = rests[r]
    rests = temprests
    # 最初の stateDict を作る
    stateDict = {"before":[], "after":[], "fname":[]}
    for fname in rests:
        fdata = datas[fname]
        stateDict["before"].append(fdata[rests[fname].pop(0)])
        stateDict["after" ].append(fdata[rests[fname].pop(0)])
        stateDict["fname" ].append(fname)
    while True:
        # rests が空なら終了
        flg = True
        for fname in rests:
            if len(rests[fname]) != 0:
                flg = False
                break
        if flg == True:
            break

        # サンプリングを用いて vp を取得
        vp = manager.getViewPointwithSampling(stateDict, sampleSize, n_iter)
        print("get vp:" + str(vp[0]["base"]) + "," + str(vp[0]["ref"]))

        # これをもとに predicts を作成
        predicts = {}
        moved = manager.getMovedObject(stateDict)
        for i in range(len(stateDict["before"])):
            # step を使う場合は -1
            predicts[stateDict["fname"][i]] = getAdditionalIntermediate(datas[stateDict["fname"][i]], stateDict["before"][i]["step"]-1, vp)
        # predicts と after の関係から，動作を決定する
        matching = {"before":[], "after":[], "fname":[]}
        pending = {}

        for i in range(len(stateDict["before"])):
            # predicts と after の差が score の一定倍程度なら
            # matching として保存
            matching["before"].append(stateDict["before"][i]) 
            matching["after" ].append(predicts[stateDict["fname"][i]]) 
            matching["fname" ].append(stateDict["fname" ][i]) 
            # 新手法は matching すべてに対して predicts を適用していくという
            # ものなので，ignored に対して特別な処理はしない
            # pending であるもののみ，rests に返却するために保存する
            if manager.calcDifference(predicts[stateDict["fname"][i]], stateDict["after"][i], objs=moved) >= vp[0]["score"] * distError and predicts[stateDict["fname"][i]]["step"] < stateDict["after"][i]["step"]:
                    pending[stateDict["fname"][i]] = stateDict["after"][i]["step"]
        # rests に pending を返却
        for fname in pending:
            # インデックスのずれを修正するために -1
            rests[fname] = [pending[fname]-1] + rests[fname]

        # output に matching と pending を追加
        output["matching"].append(matching)
        output["pending" ].append(pending)
        with open("tmp/log_MakerMain/dills/DP_main_2_temp.dill", "wb") as f:
            dill.dump(output, f)
 
       # 次の stateDict を作る
        stateDict = {"before":[], "after":[], "fname":[]}
        for fname in rests:
            fdata = datas[fname]
            stateDict["before"].append(predicts[fname])
            if len(rests[fname]) > 0:
                stateDict["after" ].append(fdata[rests[fname].pop(0)])
            else:
                print("EMPTY - " + fname)
                stateDict["after" ].append(fdata[-1])
            stateDict["fname" ].append(fname)
 
    return output

if __name__ == "__main__":
    filepaths = glob.glob("tmp/log_MakerMain/*")
    # データ取得
    datas = manager.getStateswithViewPoint(filepaths, [], [])
    with open("tmp/log_MakerMain/dills/DP_main_results.dill", "wb") as f:
        dill.dump(DP_main_2(datas, getInterDict("3-2500-2500-11-5-1")), f)
