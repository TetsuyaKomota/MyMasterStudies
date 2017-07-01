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

# ==================================================================
# 結果測定用のメソッド
    
    # 比較用のランダムなヒストグラムを生成する
def generate_random_hist (inputList, numofSample):
    output = []
    # print("HMM_test : generate_random_hist : inputList")
    # print(inputList)
    for _ in range(numofSample):
         # 境界の場所を探す 
        div = int(random.random() * len(inputList))
        idx = div
        tempMin = -1
        while True:
            if idx <= 0:
                tempMin = 2 * len(inputList)
                break
            #
            if inputList[idx] != inputList[idx-1]:
                tempMin = abs(div - idx)
                break
            else:
                idx = idx - 1
           #
        #
        idx = div 
        while True:
            if idx+1 >= len(inputList):
                break
            #
            if inputList[idx] != inputList[idx+1]:
                tempMin = min(tempMin, abs(div - idx+1))
                break
            else:
                idx = idx + 1
           #
        #
        output.append(tempMin)
    #
    '''
    plt.hist(output, bins = len(inputList))
    plt.show()
    print(output)
    '''
    return output


# ==================================================================
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
    

    # 符号化後の境界と本当の境界との距離をヒストグラムで表示する関数
def experiment_1(n_components, dataLength, div):
    print("HMM_test : experiment_1 : start")
    result = []
    score = []
    result.append(0)
    for step in range(1000):
        print("HMM_test : experiment_1 : STEP " + str(step))
        # データを生成
        print("HMM_test : experiment_1 : making data ")
        datas = []
        datas.extend(makeData(testfunc_circle, div, 0, 2*np.pi, 10))
        datas.extend(makeData(testfunc_sigmoid, dataLength - div, 0, 600, 10))
        # datas.extend(makeData(testfunc_cubic, 100, 0, 2*np.pi, 0.1))
        # モデルを生成
        model = hmm.GaussianHMM(n_components=n_components, covariance_type="diag")    
        print("HMM_test : experiment_1 : fitting model")
        model.fit(datas[0:dataLength])
        # 符号化
        print("HMM_test : experiment_1 : predict label")
        res = model.predict(datas[0:dataLength])
        # 境界の場所を探す 
        print("HMM_test : experiment_1 : counting div")
        idx = div
        tempMin = -1
        while True:
            if res[idx] != res[idx-1]:
                tempMin = abs(div - idx)
                break
            else:
                idx = idx - 1
            #
        #
        idx = div
        while True:
            if res[idx] != res[idx+1]:
                tempMin = min(tempMin, abs(div - idx+1))
                break
            else:
                idx = idx + 1
            #
        #
        # ヒストグラムに加える
        result.append(tempMin)
        print("HMM_test : experiment_1 : get pbobability")
        # tempMin が乱択されたヒストグラムに対して有意な値であるか検証
        #   ・res を用いてランダムなヒストグラムを生成
        randomHist = generate_random_hist(res, 10000)
        #   ・ヒストグラムをもとにガウス分布を生成
        myu = sum(randomHist)/len(randomHist)
        var = np.var(np.array(randomHist))
        #   ・生成された ガウス分布のパラメータを用いてtempMin の生成確立を算出
        tempScore = 1/math.sqrt(2 * math.pi * var) * math.exp(-1*(tempMin - myu) * (tempMin - myu) / var)
        # 記録
        score.append(tempScore)
    #
    # ヒストグラムを書く
    print("HMM_test : experiment_1 : result (the set of distance between truth and estmated div)")
    print(result)
    plt.hist(result, bins = dataLength)
    plt.title("result")
    plt.show()
    print("HMM_test : experiment_1 : score (the set of probability that the estimated div was picked from random-Hist)")
    print(score)
    plt.hist(score, bins = dataLength)
    plt.title("score")
    plt.show()
    print("experiment_1 : Successfully terminated.")



if __name__ == "__main__":
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        experiment_0()
        # experiment_1(30, 200, 100)
        # generate_random_hist([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4], 1000)
