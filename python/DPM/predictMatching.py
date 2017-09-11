# coding = utf-8

import DPM.ViewPointManager as manager
import copy
import numpy as np
import glob

# 途中状態列を引数に，可能な前後組をすべて取得する
def getAllPair(datas):
    output = {}
    output["before"] = []
    output["after"]  = []
    for d in datas:
        for bIdx in range(0, len(datas[d])):
            for aIdx in range(bIdx+1, len(datas[d])):
                output["before"].append(datas[d][bIdx])
                output["after"].append(datas[d][aIdx])
    return output
# 状態のペアのリストを引数に，一つ抜き法で学習し，
# 評価値と最も悪いデータを返す
#   stateDict = {"before":[前状態], "after":[後状態]}
#   return : dict:
#       score      : float : 評価値
#       worstIndex : int   : 最も悪いデータのidx
#       worstScore : float : 最も悪いデータの評価値
def getWorstData(stateDict):
    print("[predictMatching]getWorstData:start")
    output = {}
    output["score"]      = 0
    output["worstIndex"] = -1
    output["worstScore"] = 0
    for i in range(len(stateDict["before"])):
        log = "step " + str(i) + "/" + str(len(stateDict["before"]))
        print("[predictMatching]getWorstData:" + log)
        # 学習データをコピーし，テストデータ分をポップ
        tempDict = copy.deepcopy(stateDict)
        tempTest = {}
        tempTest["before"] = tempDict["before"].pop(i)
        tempTest["after"]  = tempDict["after"].pop(i)
        # 学習データで学習を行う
        vp        = manager.getViewPoint(tempDict)
        # 学習した観点でテストデータの推定を行う
        predicted = manager.predictwithViewPoint(tempTest["before"], vp)
        # 推定結果と実際の状態とのずれを計算する
        error = 0
        for o in manager.objList:
            """
            print("[predictMatching]getWorstData:o")
            print("[predictMatching]getWorstData:" + str(o))
            print("[predictMatching]getWorstData:predicted")
            print("[predictMatching]getWorstData:"+str(predicted))
            print("[predictMatching]getWorstData:tempTest['after']")
            print("[predictMatching]getWorstData:"+str(tempTest["after"]))
            """
            error += np.linalg.norm(predicted[o]-tempTest["after"][o])
        # ずれが最大を更新したら記録する
        output["score"] += error
        if error > output["worstScore"]:
            output["worstIndex"] = i
            output["worstScore"] = error
    # score は平均化
    output["score"] /= len(stateDict["before"])
    return output

if __name__ == "__main__":
    dirpath = "tmp/log_MakerMain/GettingIntermediated/3-2500-2500-9/*"
    filepaths = glob.glob(dirpath)
    datas = manager.getStateswithViewPoint(filepaths, [], [])
    stateDict = getAllPair(datas)
    worstData = getWorstData(stateDict)
    print(worstData)
