# -*- coding: utf-8 -*-

import numpy as np
import warnings
from hmmlearn import hmm

import MakeData

"""
2017/ 7/1
通常の HMM を用いて符号化を行う実験用のコード
学習に使う時系列データは MakeData.py で生成
"""

# テスト関数

    # とりあえず試してみるだけの奴．
def experiment_0(detail=False):

    # datas = MakeData.make2()

    dataList = []
    dataList.append(MakeData.make1())
    dataList.append(MakeData.make2(init=dataList[-1][-1]))
    dataList.append(MakeData.make3(init=dataList[-1][-1]))
    dataList.append(MakeData.make4(init=dataList[-1][-1]))

    lengths = []
    for d in dataList:
        lengths.append(len(d))

    datas = np.concatenate(dataList)

    MakeData.showData(datas, detail)

    model = hmm.GaussianHMM(n_components=20, covariance_type="full")    
    
    # model.fit(datas)
    model.fit(datas, lengths)
    
    # 学習結果を表示
    if detail == True:
        print("startprob_")
        print(model.startprob_)
        print("means_")
        print(model.means_)
        print("covars_")
        print(model.covars_)
        print("transmat_")
        print(model.transmat_)    

    # 推定．連続する同状態はカットして，遷移の様子だけ取り出す
    print("dataList:")
    pre = model.predict(datas)
    result = []
    for p in pre:
        if len(result) == 0 or p != result[-1]:
            result.append(p) 
    print(result)

    # データを取り直す
    dataList = []
    dataList.append(MakeData.make1())
    dataList.append(MakeData.make2(init=dataList[-1][-1]))
    dataList.append(MakeData.make3(init=dataList[-1][-1]))
    dataList.append(MakeData.make4(init=dataList[-1][-1]))

    lengths = []
    for d in dataList:
        lengths.append(len(d))

    datas = np.concatenate(dataList)

    for i, d in enumerate(dataList):
        print("dataList[" + str(i) + "]:")
        pre = model.predict(d)
        result = []
        for p in pre:
            if len(result) == 0 or p != result[-1]:
                result.append(p) 
        print(result)
   
    # makeData し直して推定した場合の状態遷移列を比較したい
    for _ in range(1000):
        # datas = MakeData.make2_half()
        datas = MakeData.make3_half()
        pre = model.predict(datas)
        result_2 = []
        for p in pre:
            if len(result_2) == 0 or p != result_2[-1]:
                result_2.append(p) 
        # print(result)
        if result != result_2:
            print("Different")
            print(result_2)
            break
    
if __name__ == "__main__":
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        experiment_0(True)
