# -*- coding: utf-8 -*-
"""
Created on Wed Jan 18 13:56:15 2017

@author: komot
"""

import numpy as np
import time
from hmmlearn import hmm
import scipy.stats as ss
import copy
import matplotlib.pyplot as plt


# ====================================================================================
# データを適当に作る

def testfunc_circle(x):
    scale = 200
    return [scale * np.sin(x), scale * np.cos(x)]

def testfunc_cubic(x):
    a = 1
    b = -10
    c = -1
    d = 1
    
    return [x, a*x*x*x + b*x*x + c*x + d]

def testfunc_sigmoid(x):
    scale = 200
    range = 50
    return [x, scale*(1 - 1/(1+np.exp(-(x-300)/range)))]


def makeData(func, size, start, end, noize):
    output = []
    
    x = start
    delta = (end - start)/size
    
    pdf = ss.norm(scale = noize)    
    
    for i in range(size):
        
        temp = func(x)
        
        for j in range(len(temp)):
            ep = pdf.rvs()
            temp[j] = temp[j] + ep
        output.append(copy.deepcopy(temp))
        x = x + delta
        
    return output
# ====================================================================================
# テスト関数

    # とりあえず試してみるだけの奴．
def experiment_0():
    datas = []
    datas.extend(makeData(testfunc_circle, 100, 0, 2*np.pi, 10))
    datas.extend(makeData(testfunc_sigmoid, 100, 0, 600, 10))
    # datas.extend(makeData(testfunc_cubic, 100, 0, 2*np.pi, 0.1))

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
    
    model = hmm.GaussianHMM(n_components=30, covariance_type="full")    
    
    model.fit(datas[0:200])
    
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

    # 推定.実際の変わり目である100番目,101番目にカッコを付ける
    pre = model.predict(datas[0:200])
    print(pre[0:100])
    print("(", end="")
    print(pre[100:102], end="")
    print(")")
    print(pre[102:])
    '''
    # 学習したモデルからサンプリングしてみる
    for _ in range(10):
        sampleX, sampleZ = model.sample(200)
        sample = np.array(sampleX).T
        plt.plot(sample[0], sample[1])
    plt.show()
    '''   

    # 符号化後の境界と本当の境界との距離をヒストグラムで表示する関数
def experiment_1(n_components, dataLength, div):
    result = []
    result.append(0)
    for _ in range(100):
        # データを生成
        datas = []
        datas.extend(makeData(testfunc_circle, div, 0, 2*np.pi, 10))
        datas.extend(makeData(testfunc_sigmoid, dataLength - div, 0, 600, 10))
        # datas.extend(makeData(testfunc_cubic, 100, 0, 2*np.pi, 0.1))
        # モデルを生成
        model = hmm.GaussianHMM(n_components=n_components, covariance_type="full")    
        model.fit(datas[0:dataLength])
        # 符号化
        res = model.predict(datas[0:dataLength])
        # 境界の場所を探す 
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
    #
    # ヒストグラムを書く
    print(result)
    plt.hist(result, bins = dataLength)
    plt.show()
    print("Successly terminated.")



if __name__ == "__main__":
    # experiment_0()
    experiment_1(30, 200, 100)
