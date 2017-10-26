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

# 全データと境界列から，マッチング群を推定して返す
# interDict : dict : ファイル名をキー，境界のステップ数のリストを持つ辞書
def DP_main(datas, interDict, sampleSize=0.5, n_iter=5000, distError=0.005):
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
        vp = manager.getViewPointwithSampling(stateDict,sampleSize,n_iter)
        print("get vp:" + str(vp["base"]) + "," + str(vp["ref"]))

        pending  = {}
        matching = {"before":[], "after":[], "fname":[]}
        moved = manager.getMovedObject(stateDict)
        
        for i in range(len(stateDict["before"])):
            # この i は「各ファイルの」という意味である
            # ファイル名は fname に i のインデックスで入っているので
            # 分かりやすいようにここで取得しておく
            fname  = stateDict["fname" ][i]
            before = stateDict["before"][i]
            after  = stateDict["after" ][i]
            
            # vp を用いて，境界の推定をやり直す
            bStep  = before["step"]
            addInter = getAdditionalIntermediate(datas[fname], bStep, vp)

            # matching の更新
            matching["before"].append(before) 
            matching["after" ].append(addInter) 
            matching["fname" ].append(fname) 
           
            # pending の更新
            # 最初の条件は，「predict よりもほんのちょっと後ろの after を
            # 次の境界としない」為の条件
            # または「正しい after だった」場合に
            # ちゃんと動くようにするためのもの
            # predict からある程度以上離れていれば，次の境界とする
            d = manager.calcDifference(addInter, after, objs=moved)
            if d >= vp["score"] * distError \
                    and addInter["step"] < after["step"] :
                pending[fname] = after["step"]

        # rests に pending を返却
        for fname in pending:
            rests[fname] = [pending[fname]] + rests[fname]

        # output に matching と pending を追加
        output["matching"].append(matching)
        output["pending" ].append(pending)
        with open("tmp/log_MakerMain/dills/DP_main_temp.dill", "wb") as f:
            dill.dump(output, f)
 
       # 次の stateDict を作る
        stateDict = {"before":[], "after":[], "fname":[]}
        for fname in rests:
            fdata = datas[fname]
            # 次の before は今の matching の after
            idx   = matching["fname"].index(fname)
            stateDict["before"].append(matching["after"][idx])
            if len(rests[fname]) > 0:
                stateDict["after"].append(fdata[rests[fname].pop(0)])
            else:
                # print("EMPTY - " + fname)
                stateDict["after" ].append(fdata[-1])
            stateDict["fname"].append(fname)

    # debug : 各 matching の平均と分散を計算する
    for i, m in enumerate(output["matching"]):
        mv = calcMeanandVarianceofMatching(m)
        line  = "matching ID:" + str(i)
        line += "\tmean("   + str(mv["mean"]["before"])
        line += "\t--> "    + str(mv["mean"]["after"])
        line += "\t), var(" + str(mv["var" ]["before"])
        line += "\t--> "    + str(mv["var" ]["after"])
        line += "\t)" 
        print(line)

    return output

def calcMeanandVarianceofMatching(matching):
    size = len(matching["before"])
    mean = {}
    Q    = {}
    var  = {}
    for ba in ["before", "after"]:
        stepList = [s["step"] for s in matching[ba]]
        mean[ba] = sum(stepList)/size
        Q[ba]    = sum([step**2 for step in stepList])/size
        var[ba]  = Q[ba] - mean[ba]**2
    return {"mean":mean, "var":var}

if __name__ == "__main__":
    filepaths = glob.glob("tmp/log_MakerMain/*")
    # データ取得
    datas = manager.getStateswithViewPoint(filepaths, [], [])
    with open("tmp/log_MakerMain/dills/DP_main_results.dill", "wb") as f:
        dill.dump(DP_main(datas, getInterDict("CHEATNANODA_results")), f)
