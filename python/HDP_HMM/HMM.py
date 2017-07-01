# -*- coding: utf-8 -*-

import numpy as np
import random
import math
import warnings
import time
from hmmlearn import hmm
import scipy.stats as ss
import copy
import matplotlib.pyplot as plt

import MakeData

"""
2017/ 7/1
通常の HMM を用いて符号化を行う実験用のコード
学習に使う時系列データは MakeData.py で生成
"""

# テスト関数

    # とりあえず試してみるだけの奴．
def experiment_0():
    datas = MakeData.make1()

    for _ in range(10):
        # datas.extend(makeData(testfunc_circle, 100, 0, 2*np.pi, 10))
        # datas.extend(makeData(testfunc_cubic, 100, 0, 2*np.pi, 0.1))
        print(datas)
        # datas.append(np.array(data))
        # 転置
        invdata = np.array(datas).T
        print(invdata)
        
        plt.plot(invdata[0], invdata[1])
    plt.show()
    
    model = hmm.GaussianHMM(n_components=10, covariance_type="full")    
    
    model.fit(datas)
    
    '''
    # 学習結果を表示
    print("startprob_")
    print(model.startprob_)
    print("means_")
    print(model.means_)
    print("covars_")
    print(model.covars_)
    print("transmat_")
    print(model.transmat_)    
    '''

    # 推定．連続する同状態はカットして，繊維の様子だけ取り出す
    pre = model.predict(datas)
    result = []
    for p in pre:
        if len(result) == 0 or p != result[-1]:
            result.append(p) 
    print(result)
   
    # makeData し直して推定した場合の状態遷移列を比較したい
    for _ in range(1000):
        datas = MakeData.make1_half()
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
        experiment_0()
