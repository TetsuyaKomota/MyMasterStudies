# -*- coding: utf-8 -*-

import numpy as np
import warnings
import dill
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

    methods = []
    methods.append(MakeData.make1)
    methods.append(MakeData.make2)
    methods.append(MakeData.make3)
    methods.append(MakeData.make4)

    dataList = []
    for m in methods:
        # とりあえず各軌道2回ずつ取得して学習データに使う
        for _ in range(2):
            dataList.append(m())

    lengths = []
    for d in dataList:
        lengths.append(len(d))

    datas = np.concatenate(dataList)

    MakeData.showData(datas, detail)

    model = hmm.GaussianHMM(n_components=30, covariance_type="full")    
    
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

    # 学習したモデルをもとに，推定を行う
    # dill 出力して，それをHPYLM で参照する
    results = {}
    for i, m in enumerate(methods):
        print("MakeData.make" + str(i+1) + ":")
        results_temp = []
        for _ in range(10):
            pre = model.predict(m())
            result = []
            for p in pre:
                if len(result) == 0 or p != result[-1]:
                    result.append(p) 
            print(result)
            results_temp.append(result)
        results["make"+str(i+1)] = results_temp
    with open("tmp/HMM_results.dill", "wb")  as f:
        dill.dump(results, f)
        print("Successfully dumping")
 
if __name__ == "__main__":
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        experiment_0(True)
