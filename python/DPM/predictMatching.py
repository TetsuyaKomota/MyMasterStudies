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
    # print("[predictMatching]getAdditionalIntermediate:step:"+str(step))
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
        elif curError >= 5*tempdiff:
            break
    return output

# ディレクトリ名を指定して，ファイル名をキー，
# 境界のidx リストを値とする辞書を作る
def getInterDict(dirname):
    output  = {}
    if dirname == "CHEATNANODA_results":
        dirpath = "tmp/CHEATNANODA_results/*"
    else:
        dirpath = "tmp/log_MakerMain/GettingIntermediated/"+dirname+"/*"
    fpaths = glob.glob(dirpath)
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
                output[fname].append(int(line.split(",")[0]))
    return output

# 境界情報をならす
# 10ステップ以上近すぎる境界は一つにまとめる
def pruningInterDict(interdict):
    output = {}
    for fname in interdict.keys():
        temp = []
        for s in interdict[fname]:
            temp.append(s)
            if len(temp)>1 and np.abs(temp[-1]-temp[-2])<20:
                temp.append(int((temp.pop()+temp.pop())/2))
        output[fname] = temp
    return output

# 全データと境界列から，境界列を剪定する
# よく考えれば 100 と 300 と 500 付近の境界は「hand 以外の環境に変化がない」
# ので，0-100, 200-300, 400-500 の動作はそもそも学習し得ない
# 境界の前後で環境がほとんど変化しない場合，あとの境界を interDict から削除する
def pruningInterDict(datas, interDict):
    output = {}
    print(interDict)
    for filename in interDict.keys():
        output[filename] = []
        before = None
        after  = None
        for step in interDict[filename]:
            after  = datas[filename][step]
            # 目測で大体 4500 前後
            if len(output[filename]) == 0 or manager.calcDifference(before, after) > 4500:
                output[filename].append(step)
                before = datas[filename][step]
                

# interDict : dict : ファイル名をキー，境界のステップ数のリストを持つ辞書
# あまりに実装がダサいので作り直した
def DP_main(datas, interDict_, sampleSize=0.7, n_iter=50, distError=50):
    interDict = pruningInterDict(datas, interDict_)
    output = {"matching":[], "viewpoint":[]}
    rests = copy.deepcopy(interDict)
    # 最初の stateDict を作る
    stateDict = {}
    for fname in rests.keys():
        fdata = datas[fname]
        stateDict[fname] = fdata[rests[fname].pop(0)]
    # matching に登録する
    output["matching" ].append(stateDict)
    output["viewpoint"].append(None)
    while True:
        # rests が空なら終了
        flg = True
        for fname in rests.keys():
            if len(rests[fname]) != 0:
                flg = False
                break
        if flg == True:
            break
        # 次の stateDict を作る
        stateDict = {}
        for fname in rests.keys():
            fdata = datas[fname]
            while True:
                if len(rests[fname])>0 and rests[fname][0] < output["matching"][-1][fname]["step"]+10:
                    rests[fname].pop(0) 
                else:
                    break
            if len(rests[fname]) > 0:
                stateDict[fname] = fdata[rests[fname].pop(0)]
            else:
                # print("EMPTY - " + fname)
                stateDict[fname] = fdata[-1]

        # サンプリングを用いて vp を取得
        fnameList  = sorted(list(stateDict.keys()))
        beforeDict = output["matching"][-1]
        beforeList = [beforeDict[fn] for fn in fnameList]
        afterList  = [stateDict[fn]  for fn in fnameList]
        tempDict   = {"before":beforeList, "after":afterList, "fname":fnameList}

        vp = manager.getViewPointwithSampling(tempDict,sampleSize,n_iter)
        print("get vp:" + str(vp["base"]) + "," + str(vp["ref"]))

        matching = {}
        moved = manager.getMovedObject(tempDict)
        
        for fname in stateDict.keys():
            # vp を用いて，境界の推定をやり直す
            bStep  = output["matching"][-1][fname]["step"]
            addInter = getAdditionalIntermediate(datas[fname], bStep, vp)
            # matching の更新
            matching[fname] = addInter

        # output に matching と pending と vp を追加
        output["matching" ].append(matching)
        output["viewpoint"].append(vp)

    with open("tmp/log_MakerMain/dills/DP_main_temp.dill", "wb") as f:
        dill.dump(output, f)
    return output


def debug_calcMeanandVarianceofMatching(matching):
    size = len(matching["before"])
    mean = {}
    Q    = {}
    var  = {}
    for ba in ["before", "after"]:
        stepList = [s["step"] for s in matching[ba]]
        mean[ba] = sum(stepList)/size
        Q[ba]    = sum([step**2 for step in stepList])/size
        var[ba]  = Q[ba] - mean[ba]**2
    line  = "\tmean("   + str(mean["before"])
    line += "\t--> "    + str(mean["after"])
    line += "\t), var(" + str(var["before"])
    line += "\t--> "    + str(var["after"])
    line += "\t)" 
    return line

if __name__ == "__main__":
    filepaths = glob.glob("tmp/log_MakerMain/*")
    # データ取得
    datas = manager.getStateswithViewPoint(filepaths, [], [])
    with open("tmp/log_MakerMain/dills/DP_main_results.dill", "wb") as f:
        dill.dump(DP_main(datas, getInterDict("CHEATNANODA_results")), f)
