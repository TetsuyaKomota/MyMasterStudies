#-*- coding: utf-8 -*-

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


# =====================================================================
# データのプリミティブ．
# これを直接叩くことはなく,必ず makeData の引数に使用する

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

# =====================================================================
# func を組み合わせてあらかじめ作ったプリセットデータ生成メソッド
# 外部からは基本これを叩くだけ

# 右回り円運動 → 右下がり順方向シグモイド
# →右下がり逆方向シグモイド → 右回り円運動
# 各 100 ステップで 400ステップデータ
def make1():
    datas = []
    datas.extend(makeData(testfunc_circle, 100, 0, 2*np.pi, 10))
    datas.extend(makeData(testfunc_sigmoid, 100, 0, 600, 10))
    datas.extend(makeData(testfunc_sigmoid, 100, 600, 0, 10))
    datas.extend(makeData(testfunc_circle, 100, 0, 2*np.pi, 10))
    return datas

# 右回り円運動 → 右下がり順方向シグモイド
# 各 100 ステップで 200ステップデータ
# つまり make1 の前半のみ
def make1_half():
    datas = []
    datas.extend(makeData(testfunc_circle, 100, 0, 2*np.pi, 10))
    datas.extend(makeData(testfunc_sigmoid, 100, 0, 600, 10))
    return datas

# =====================================================================
# 機能系メソッド
# いじらない

# 引数に与えられた関数で start から end まで等間隔で size 個のデータを
# 分散 noize のガウス誤差を付与して獲得する
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

# 取得したデータを可視化
def showData(datas, detail=False):
    # 転置
    invdata = np.array(datas).T
    if detail == True:
        print(datas)
        print(invdata)
    plt.plot(invdata[0], invdata[1])
    plt.show()
 
# =====================================================================
