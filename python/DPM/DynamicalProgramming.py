# coding = utf-8

# TODO predictMatching と合体していいかも

import DPM.predictMatching as matching
import DPM.ViewPointManager as manager
import numpy as np
import glob

RANGE = 1500

# 状態列と開始ステップと観点モデルを引数に，
# 追加で推定される途中状態に最も近い状態を返す
def getAdditionalIntermediate(stateList, step, viewPoint, detail=False):
    # 指定したステップ番号のデータを取得する
    bState = stateList[step]
    # 取得したデータに対して次の状態を予測する
    aState = manager.predictwithViewPoint(bState, viewPoint)
    # 予測した状態に最も近い状態を stateList から推定する
    output = None
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
        elif curError >= tempdiff + RANGE:
            break
    return output

if __name__ == "__main__":
    filepaths = glob.glob("tmp/log_MakerMain/*")
    # データ取得
    datas = manager.getStateswithViewPoint(filepaths, [], [])
    stateDict = {}
    stateDict["before"] = []
    stateDict["after"]  = []
    for count, d in enumerate(datas):
        stateDict["before"].append(datas[d][0])
        stateDict["after"].append(datas[d][100])
        if count >= 49:
            testname = d
            break
    # テストデータを一件だけ取る
    test = {}
    test["before"] = stateDict["before"].pop()
    test["after"]  = stateDict["after"].pop()
    # 学習する
    vp = manager.getViewPoint(stateDict)
    # 元データの50 番に対して AdditionalIntermediate を適用する
    testStateList = datas[testname]
    additional = getAdditionalIntermediate(testStateList,0,vp,detail=True)
    print(additional["step"])
