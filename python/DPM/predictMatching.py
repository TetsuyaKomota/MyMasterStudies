# coding = utf-8

import DPM.ViewPointManager as manager
import copy
import numpy as np
import glob
import dill 

THRESHOLD = 2000

# 途中状態列を引数に，可能な前後組をすべて取得する
def getAllPair(datas):
    output = {}
    output["before"] = []
    output["after"]  = []
    for d in datas:
        for bIdx in range(0, len(datas[d])):
            for aIdx in range(bIdx+1, bIdx+4):
                if aIdx >= len(datas[d]):
                    continue
                range(bIdx+1, len(datas[d]))
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
            print("[predictMatching]getWorstData:   updateWorst")
            output["worstIndex"] = i
            output["worstScore"] = error
    # score は平均化
    output["score"] /= len(stateDict["before"])
    return output

# 状態の前後の組を引数に．マッチングを推定する
# getWorstData を求め，score が高ければworstIdx のデータをポップし，
# 低くなったらそれをマッチングとする
#   stateDict = {"before":[前状態], "after":[後状態]}
def getMatching(stateDict):
    f = open("tmp/predictMatching.txt", "w", encoding="utf-8")
    output = []
    rest = copy.deepcopy(stateDict)
    while True:
        if len(rest["before"]) == 0:
            break
        current = copy.deepcopy(rest)
        rest = {"before":[], "after":[]}
        while True:
            result = getWorstData(current)
            print("result:"+str(result))
            f.write(str(result)+"\n")
            if result["score"] < THRESHOLD or len(current["before"]) < 3:
                break
            rest["before"].append(current["before"].pop(result["worstIndex"]))
            rest["after"].append(current["after"].pop(result["worstIndex"]))
        output.append(current)
    f.close()
    return output

if __name__ == "__main__":
    filepaths = glob.glob("tmp/log_MakerMain/*")
    # データ取得
    datas = manager.getStateswithViewPoint(filepaths, [], [])
    """
    # 0 番と 100 番のデータのみを取り出してみる
    stateDict = {}
    stateDict["before"] = []
    stateDict["after"]  = []
    flag = False
    for d in datas:
        stateDict["before"].append(datas[d][0])
        stateDict["after"].append(datas[d][100])
        # 一個だけ, 200番と 300番のデータを入れてみる
        if flag == False:
            stateDict["before"].append(datas[d][200])
            stateDict["after"].append(datas[d][300])
            flag = True
    worstData = getWorstData(stateDict)
    # idx = 1 になってくれると成功 → なった
    print(worstData)
    """
    # getMatching のテスト
    # 0,100 ペアと 200, 300 ペアを取り出す
    stateDict = {}
    stateDict["before"] = []
    stateDict["after"]  = []
    flag = False
    for count, d in enumerate(datas):
        if count >= 50:
            break
        stateDict["before"].append(datas[d][0])
        stateDict["after"].append(datas[d][100])
        if True or count%3==0:
            stateDict["before"].append(datas[d][200])
            stateDict["after"].append(datas[d][300])
    # マッチングを予測
    matching = getMatching(stateDict)
    # 分けられていれば成功
    print(matching)
    with open("tmp/log_MakerMain/dills/predictMatching_results.dill", "wb")  as f:
        dill.dump(matching, f)
