import random
import DPM.ViewPointManager as manager
import glob

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


# 全データと境界列から，マッチング群を推定して返す
# interDict : dict : ファイル名をキーに，境界状態のステップ数のリストを持つ辞書
def DP_main(datas, interDict):
    output = {"matching":[], "pending":[]}
    rests = copy.deepcopy(interDict)
    # 境界が 0 番, 500番以外にないデータはここで除外する
    temprests = {}
    for r in rests:
        if len(rests[r]) > 2:
            temprests[r] = rests[r]
    rests = temprests
    # 最初の stateDict を作る
    stateDict = {"before":[], "after":[], "fname":[], "isadd":[]}
    for fname in rests:
        fdata = datas[fname]
        stateDict["before"].append(fdata[rests[fname].pop(0)])
        stateDict["after" ].append(fdata[rests[fname].pop(0)])
        stateDict["fname" ].append(fname)
        stateDict["isadd" ].append(False)
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
        vp = manager.getViewPointwothSampling(stateDict)

        # これをもとに predicts を作成
        predicts = {}
        moved = manager.getMovedObject(stateDict)
        for i in range(len(stateDict["before"])):
            predicts[stateDict["fname"][i]] = getAdditionalIntermediate(datas[pending["fname"][i]], pending["before"][i]["step"], vp)
        # predicts と after の関係から，動作を決定する
        matching = {"before":[], "after":[], "fname":[], "isadd":[]}
        # ignored  = {"before":[], "after":[], "fname":[], "isadd":[]}
        # pending  = {"before":[], "after":[], "fname":[], "isadd":[]}
        pending = {}

        for i in range(len(stateDict["before"])):
            # predicts と after の差が score の一定倍程度なら
            # matching として保存
            if manager.calcDifference(predicts[stateDict["fname"][i]], stateDict["after"], objs=moved) < vp["score"] * 0.8:
                matching["before"].append(stateDict["before"][i]) 
                matching["after" ].append(predicts[stateDict["fname"][i]]) 
                matching["fname" ].append(stateDict["fname" ]) 
                matching["isadd" ].append(stateDict["isadd" ]) 
            # 新手法は matching すべてに対して predicts を適用していくという
            # ものなので，ignored に対して特別な処理はしない
            # pending であるもののみ，rests に返却するために保存する
            elif predicts[stateDict["fname"][i]]["step"] < stateDict["after"][i]["step"]:
                    pending[stateDict["fname"][i]] = stateDict["after"][i]["step"]
        # rests に pending を返却
        for fname in pending:
            rests[fname] = [pending[fname]] + rests[fname]

        # output に matching と pending を追加
        output["matching"].append(matching)
        output["pending" ].append(pending)

       # 次の stateDict を作る
        stateDict = {"before":[], "after":[], "fname":[], "isadd":[]}
        for fname in rests:
            fdata = datas[fname]
            stateDict["before"].append(predicts[fname])
            stateDict["after" ].append(fdata[rests[fname].pop(0)])
            stateDict["fname" ].append(fname)
            stateDict["isadd" ].append(False)
 
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
    return output



if __name__ == "__main__":
    filepaths = glob.glob("tmp/forTest_predictMatching/*")
    # filepaths = glob.glob("tmp/log_MakerMain/*")
    # データ取得
    datas = manager.getStateswithViewPoint(filepaths, [], [])
    stateDict = {}
    stateDict["before"] = []
    stateDict["after"]  = []
    stateDict["fname"]  = []
    stateDict["isadd"]  = []
    
    for count, d in enumerate(sorted(list(datas.keys()))):
        stateDict["before"].append(datas[d][0])
        stateDict["after"].append(datas[d][200])
        stateDict["fname"].append(d)
        stateDict["isadd"].append(False)
        if count >= 249:
            break
        if count >= 239:
            stateDict["before"].append(datas[d][0])
            stateDict["after"].append(datas[d][300])
            stateDict["fname"].append(d)
            stateDict["isadd"].append(False)
        if count >= 244:
            stateDict["before"].append(datas[d][0])
            stateDict["after"].append(datas[d][100])
            stateDict["fname"].append(d)
            stateDict["isadd"].append(False)
    print(manager.getViewPointwithSampling(stateDict))
 
