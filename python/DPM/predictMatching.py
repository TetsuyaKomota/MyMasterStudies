# coding = utf-8

import DPM.ViewPointManager as manager
import copy
import numpy as np
import glob
import dill 
import os
import re

# THRESHOLD = 1950
THRESHOLD = 1.7

# 途中状態列を引数に，可能な前後組をすべて取得する
def getAllPair(datas):
    output = {}
    output["before"] = []
    output["after"]  = []
    output["fname"]  = []
    for d in datas:
        for bIdx in range(0, len(datas[d])):
            for aIdx in range(bIdx+1, bIdx+4):
                if aIdx >= len(datas[d]):
                    continue
                range(bIdx+1, len(datas[d]))
                output["before"].append(datas[d][bIdx])
                output["after"].append(datas[d][aIdx])
                output["fname"].append(d)
    return output
# 状態のペアのリストを引数に，一つ抜き法で学習し，
# 評価値と最も悪いデータを返す
#   stateDict = {"before":[前状態], "after":[後状態]}
#   return : dict:
#       score      : float : 評価値
#       worstIndex : int   : 最も悪いデータのidx
#       worstScore : float : 最も悪いデータの評価値
def getWorstData(stateDict, detail=False):
    if detail == True:
        print("[predictMatching]getWorstData:start")
    output = {}
    output["score"]      = 0
    output["worstIndex"] = -1
    output["worstScore"] = 0
    for i in range(len(stateDict["before"])):
        if detail == True:
            log = "step " + str(i) + "/" + str(len(stateDict["before"]))
            print("[predictMatching]getWorstData:" + log)
        # 学習データをコピーし，テストデータ分をポップ
        tempDict = copy.deepcopy(stateDict)
        tempTest = {}
        tempTest["before"] = tempDict["before"].pop(i)
        tempTest["after"]  = tempDict["after"].pop(i)
        tempTest["fname"]  = tempDict["fname"].pop(i)
        # 学習データで学習を行う
        vp        = manager.getViewPoint(tempDict)
        # 学習した観点でテストデータの推定を行う
        predicted = manager.predictwithViewPoint(tempTest["before"], vp)
        # 推定結果と実際の状態とのずれを計算する
        error = manager.calcDifference(predicted, tempTest["after"])
        # ずれが最大を更新したら記録する
        output["score"] += error
        if error > output["worstScore"]:
            if detail == True:
                print("[predictMatching]getWorstData:   updateWorst")
            output["worstIndex"] = i
            output["worstScore"] = error
    # score は平均化
    output["score"] /= len(stateDict["before"])
    if detail == True:
        print("[predictMatching]getWorstData:score:" + str(output["score"]))
    return output

# 状態の前後の組を引数に．マッチングを推定する
# getWorstData を求め，score が高ければworstIdx のデータをポップし，
# 低くなったらそれをマッチングとする
#   stateDict = {"before":[前状態], "after":[後状態]}
def getMatchingfromAllPairs(stateDict):
    f = open("tmp/predictMatching.txt", "w", encoding="utf-8")
    output = []
    rest = copy.deepcopy(stateDict)
    while True:
        if len(rest["before"]) == 0:
            break
        current = copy.deepcopy(rest)
        rest = {"before":[], "after":[], "fname":[]}
        while True:
            result = getWorstData(current)
            print("result:"+str(result))
            f.write(str(result)+"\n")
            # if result["score"] < THRESHOLD or len(current["before"]) < 3:
            rate = result["worstScore"]/result["score"]
            print("rate:"+str(rate))
            if rate < THRESHOLD or len(current["before"]) < 3:
                break
            rest["before"].append(current["before"].pop(result["worstIndex"]))
            rest["after"].append(current["after"].pop(result["worstIndex"]))
            rest["fname"].append(current["fname"].pop(result["worstIndex"]))
        output.append(current)
    f.close()
    return output

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
        # elif curError >= tempdiff + 1500:
        elif curError >= 5*tempdiff:
            print("TOKEN")
            break
    return output

# 状態列全体と，注目している状態列の前後組から，マッチングを推定し，
# マッチングと，無視する状態と，保留の状態を返す
# 動的計画法の1ステップ分
def DP_sub(datas, stateDict):
    output = {}
    matching = {"before":[], "after":[], "fname":[]}
    ignored  = {"before":[], "after":[], "fname":[]}
    pending  = {"before":[], "after":[], "fname":[]}

    # 閾値以下になるまでworstState を抽出
    matching = copy.deepcopy(stateDict)
    while True:
        result = getWorstData(matching)
        
        # if result["score"] < THRESHOLD:
        rate = result["worstScore"]/result["score"]
        print("[predictMatching]DP_sub:rate:"+str(rate))
        if rate < THRESHOLD:
            break
        elif len(matching) < 3:
            print("失敗よ！ばか！")
            exit()
        pending["before"].append(matching["before"].pop(result["worstIndex"]))
        pending["after" ].append(matching["after"].pop(result["worstIndex"]))
        pending["fname" ].append(matching["fname"].pop(result["worstIndex"]))

        print("[predictMatching]DP_sub:pended:"+str(pending["after"][-1]["timelen"]))

    # 除去した状態のbefore でgetAdditional
    vp = manager.getViewPoint(matching)
    additionals = []
    for i in range(len(pending["before"])):
        additionals.append(getAdditionalIntermediate(datas[pending["fname"][i]], pending["before"][i]["step"], vp))
        temptext = "[predictMatching]DP_sub:additionals-(before, after, additional):("
        temptext += str(pending["before"][i]["step"])+", "
        temptext += str(pending["after"][i]["step"])+", "
        temptext += str(additionals[-1]["step"])+")"
        print(temptext)

    # additional のステップが after のステップよりも手前なら保留データ
    for i in range(len(additionals)):
        # 無視だろうが保留だろうが，additionals したデータは適切なので
        # additionals を用いて matching に復帰
        matching["before"].append(pending["before"][i])
        matching["after" ].append(additionals[i])
        matching["fname" ].append(pending["fname"][i])
        # additional のステップが after のステップよりも奥なら無視データ
        if additionals[i]["step"] > pending["after"][i]["step"]:
            ignored["before"].append(pending["before"][i])
            ignored["after" ].append(pending["after"][i])
            ignored["fname" ].append(pending["fname"][i])
            # pending[after] を消しておいて，あとで
            # 「消されてないのは保留データ」というように処理する
            pending["after"][i] = None
    temppend = {"before":[], "after":[], "fname":[]}
    for i in range(len(pending["before"])):
        if pending["after"][i] is not None:
            # temppend["before"].append(pending["before"][i])
            # pending の前状態は additionals で更新
            temppend["before"].append(additionals[i])
            temppend["after" ].append(pending["after"][i])
            temppend["fname" ].append(pending["fname"][i])
    pending = temppend

    # 返す
    output["matching"] = matching
    output["ignored"]  = ignored
    output["pending"]  = pending
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
def DP_main(datas, interDict):
    output = []
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
        # stateDict から DP_sub でマッチング，保留，無視を取得
        """
        print("CHECK - rests")
        for r in rests:
            print(r)
            print(rests[r])
        print("CHECK - stateDict")
        for s in stateDict:
            print(s)
            print(stateDict[s])
        """
        results = DP_sub(datas, stateDict)
        # マッチングを output に append
        output.append(results["matching"])
        with open("tmp/log_MakerMain/dills/DP_main_temp.dill", "wb") as f:
            dill.dump(output, f)
        # 無視の after をrests から消す
        # → pop してるから，何もしなければ無視することになる
        # 保留の after を rests に返す
        for i in range(len(results["pending"]["before"])):
            fname = results["pending"]["fname"][i]
            # step は 1 ずれてるので 1 引く
            rests[fname] = [results["pending"]["after"][i]["step"]-1] + rests[fname]
        # 次の stateDict を作る
        stateDict["before"] = results["matching"]["after"]
        stateDict["after" ] = []
        stateDict["fname "] = results["matching"]["fname"]
        for fname in stateDict["fname"]:
            # すでに境界状態を使い果たした（本来そうならないでほしいが）fnameを表示して無視
            if len(rests[fname]) == 0:
                print("[predictMatching]DP_main:Empty - "+fname)
                for i in range(len(stateDict["fname"])):
                    if stateDict["fname"][i] == fname:
                        stateDict["before"].pop(i)
                        stateDict["fname"].pop(i)
                        break
                continue
            fdata = datas[fname]
            stateDict["after"].append(fdata[rests[fname].pop(0)])
    return output

if __name__ == "__main__":
    # filepaths = glob.glob("tmp/forTest_predictMatching/*")
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
    """
    # getMatchingfromAllPairs のテスト
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
    matching = getMatchingfromAllPairs(stateDict)
    # 分けられていれば成功
    print(matching)
    with open("tmp/log_MakerMain/dills/predictMatching_results.dill", "wb")  as f:
        dill.dump(matching, f)
    """
    """
    stateDict = {}
    stateDict["before"] = []
    stateDict["after"]  = []
    stateDict["fname"]  = []
    
    for count, d in enumerate(sorted(list(datas.keys()))):
        stateDict["before"].append(datas[d][0])
        stateDict["after"].append(datas[d][100])
        stateDict["fname"].append(d)
        if count >= 49:
            testname = d
    # テストデータを一件だけ取る
    test = {}
    test["before"] = stateDict["before"].pop()
    test["after"]  = stateDict["after"].pop()
    test["fname"]  = stateDict["fname"].pop()
    # 学習する
    vp = manager.getViewPoint(stateDict)
    # 元データの50 番に対して AdditionalIntermediate を適用する
    testStateList = datas[testname]
    additional = getAdditionalIntermediate(testStateList,0,vp)
    print(additional["step"])
    """
    """
    stateDict = {}
    stateDict["before"] = []
    stateDict["after"]  = []
    stateDict["fname"]  = []
    
    for count, d in enumerate(sorted(list(datas.keys()))):
        stateDict["before"].append(datas[d][0])
        stateDict["after"].append(datas[d][200])
        stateDict["fname"].append(d)
        if count >= 249:
            break
        if count >= 239:
            stateDict["before"].append(datas[d][0])
            stateDict["after"].append(datas[d][300])
            stateDict["fname"].append(d)
        if count >= 244:
            stateDict["before"].append(datas[d][0])
            stateDict["after"].append(datas[d][100])
            stateDict["fname"].append(d)
    # マッチング，無視，保留の取得のテスト
    result = DP_sub(datas, stateDict)
    with open("tmp/log_MakerMain/dills/DP_sub_results.dill", "wb") as f:
        dill.dump(result, f)
    """
    with open("tmp/log_MakerMain/dills/DP_main_results.dill", "wb") as f:
        dill.dump(DP_main(datas, getInterDict("3-2500-2500-11-5-1")))
