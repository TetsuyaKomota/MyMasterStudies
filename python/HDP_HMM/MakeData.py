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

def testfunc_cos(x):
    scale = 200
    return [scale * x, scale * np.cos(x)]

def testfunc_sin(x):
    scale = 100
    return [scale * np.sin(x), scale * x]

def testfunc_invsin(x):
    scale = 100
    return [scale * np.sin(x), scale * x * (-1)] 

def testfunc_sigmoid(x):
    scale = 200
    rang  = 50
    return [x, scale*(1 - 1/(1+np.exp(-(x-300)/rang)))]

def testfunc_inve(x):
    scale = 500
    return [x, scale * (1 - np.exp(-1 * x/10))]

def testfunc_x(x):
    scale = 20
    return [scale * x, 0]

def testfunc_y(x):
    scale = 20
    return [0, scale * x]

# =====================================================================
# func を組み合わせてあらかじめ作ったプリセットデータ生成メソッド
# 外部からは基本これを叩くだけ

# 右回り円運動 → 右下がり順方向シグモイド
# →右下がり逆方向シグモイド → 右回り円運動
# 各 100 ステップで 400ステップデータ
def make1(noize=10, init=[0, 0]):
    datas = []
    datas.extend(makeData(testfunc_circle, 100,0,2*np.pi,noize,init=init))
    datas.extend(makeData(testfunc_sigmoid, 100, 0, 600, noize))
    datas.extend(makeData(testfunc_sigmoid, 100, 600, 0, noize))
    datas.extend(makeData(testfunc_circle, 100, 0, 2*np.pi, noize))
    # return datas
    # 速度に変換してみよう
    # return getVelocityList(datas)
    # TMA で平滑化してみよう
    # return getTMAList(datas)
    # TMA で平滑化した状態で速度列をとってみよう
    return getVelocityList(getTMAList(datas))

# 右回り円運動 → 右下がり順方向シグモイド
# 各 100 ステップで 200ステップデータ
# つまり make1 の前半のみ
def make1_half(noize=10, init=[0, 0]):
    datas = []
    datas.extend(makeData(testfunc_circle,100,0,2*np.pi, noize, init=init))
    datas.extend(makeData(testfunc_sigmoid, 100, 0, 600, noize))
    # return datas
    # 速度に変換してみよう
    # return getVelocityList(datas)
    # TMA で平滑化してみよう
    # return getTMAList(datas)
    # TMA で平滑化した状態で速度列をとってみよう
    return getVelocityList(getTMAList(datas))


# 上方向に順 sin → 下方向に順sin 
# つまり八文字
# 各100ステップで 200ステップデータ
def make2(noize=10, init=[0, 0]):
    datas = []
    datas.extend(makeData(testfunc_sin,100,0,2*np.pi,noize,init=init))
    datas.extend(makeData(testfunc_invsin,100,0,2*np.pi,noize,init=datas[-1]))
    # return datas
    # 速度に変換してみよう
    # return getVelocityList(datas)
    # TMA で平滑化してみよう
    # return getTMAList(datas)
    # TMA で平滑化した状態で速度列をとってみよう
    return getVelocityList(getTMAList(datas))

# 上方向に順 sin
# 100ステップデータ
def make2_half(noize=10, init=[0, 0]):
    datas = []
    datas.extend(makeData(testfunc_sin, 100, 0, 2*np.pi, noize, init=init))
    # return datas
    # 速度に変換してみよう
    # return getVelocityList(datas)
    # TMA で平滑化してみよう
    # return getTMAList(datas)
    # TMA で平滑化した状態で速度列をとってみよう
    return getVelocityList(getTMAList(datas))

# 適当な高さまで漸近 → 返ってくる
# 各 100 ステップで　200 ステップデータ
def make3(noize=10, init=[0, 0]):
    datas = []
    datas.extend(makeData(testfunc_inve, 100, 0, 500, noize, init=init))
    invdata = []
    for i in range(len(datas)):
        invdata.append(datas[-i-1])
    datas.extend(invdata)
    # return datas
    # 速度に変換してみよう
    # return getVelocityList(datas)
    # TMA で平滑化してみよう
    # return getTMAList(datas)
    # TMA で平滑化した状態で速度列をとってみよう
    return getVelocityList(getTMAList(datas))

# 適当な高さまで漸近
# 各 100  ステップデータ
def make3_half(noize=10, init=[0, 0]):
    datas = []
    datas.extend(makeData(testfunc_inve, 100, 0, 500, noize, init=init))
    # return datas
    # 速度に変換してみよう
    # return getVelocityList(datas)
    # TMA で平滑化してみよう
    # return getTMAList(datas)
    # TMA で平滑化した状態で速度列をとってみよう
    return getVelocityList(getTMAList(datas))

# S字っぽいの書いて戻ってくる
def make4(noize=10, init=[0, 0]) : 
    datas = []
    datas.extend(makeData(testfunc_x, 100, 0, -10, noize, init=init))
    datas.extend(makeData(testfunc_y, 100, 0, 5, noize, init=datas[-1]))
    datas.extend(makeData(testfunc_x, 100, 0, -10, noize, init=datas[-1]))
    datas.extend(makeData(testfunc_y, 100, 0, -5, noize, init=datas[-1]))
    datas.extend(makeData(testfunc_x, 100, 0, 20, noize, init=datas[-1]))
    # return datas
    # 速度に変換してみよう
    # return getVelocityList(datas)
    # TMA で平滑化してみよう
    # return getTMAList(datas)
    # TMA で平滑化した状態で速度列をとってみよう
    return getVelocityList(getTMAList(datas))


 

# =====================================================================
# 機能系メソッド
# いじらない

# 引数に与えられた関数で start から end まで等間隔で size 個のデータを
# 分散 noize のガウス誤差を付与して獲得する
def makeData(func, size, start, end, noize, init=[0, 0]):
    output = []
    
    x = start
    delta = (end - start)/size
    
    pdf = ss.norm(scale = noize)    
    
    for i in range(size):
        
        temp = func(x)
        
        for j in range(len(temp)):
            ep = pdf.rvs()
            temp[j] = temp[j] + ep
        output.append(np.array(copy.deepcopy(temp))+np.array(init))
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

# 取得したデータを速度列に変換
def getVelocityList(datas, timeDelta=0.01):
    output = []
    prev = np.array(datas[0])
    for d in datas[1:]:
        output.append((np.array(d)-prev)/timeDelta)
        prev = d
    # 長さを datas と合わせる
    output.append(output[-1])
    return output

# 取得したデータを単純移動平均で平滑化
# 前後 length の平均をとるので，範囲は 2*length
# 両端のデータはそれぞれ片側の平均しか取れない(取らない)
def getSMAList(datas, length=10):
    output = []
    # バッファ．こいつに足したり引いたりする
    buf = np.zeros(len(datas[0]))
    # バッファに保持されているデータの数
    count = 0
    # まず右側の平均を取得する
    for l in range(length+1): # 自分を含めるために +1
        if len(datas) > l:
            count = count + 1
            buf = buf + np.array(datas[l])
        else:
            break
    # 移動平均を計算する
    for idx in range(len(datas)):
        # データを取得する
        output.append(buf/count)
        # 移動する
        # 現在のデータは次のデータの左側となるので，加える
        # count = count + 1
        # buf = buf + datas[idx]
        # 左側のデータ数が既にlength 個あるなら，移動する際に一つ取り除く
        if idx >= length:
            count = count - 1
            buf = buf - np.array(datas[idx-length])
        # 右側のデータ数が length 以上ある場合は buf に加える
        # idx+length までは含まれているから，その次ということで +1
        if idx+length+1 < len(datas):
            count = count + 1
            buf = buf + np.array(datas[idx+length+1])
    return output 

# 取得したデータを三角移動平均で平滑化
def getTMAList(datas, length=10):
    output = []
    half_length = math.ceil((length+1)/2)
    output = getSMAList(getSMAList(datas, half_length), half_length)
    return output


# =====================================================================
