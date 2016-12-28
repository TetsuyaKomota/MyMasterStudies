# -*- coding: utf-8 -*-
"""
Created on Wed Dec 28 13:59:17 2016

@author: komot
"""

import scipy.stats as ss
import numpy as np
import GMMv2 as gmm
import CRP
import math

class DPM:
    def __init__(self, alpha=1.0, beta=1/3, df=15, scale=np.matrix([[1.0, 0], [0, 0.1]])):
        self.beta = beta
        self.df = df
        self.scale = scale
        self.crp = CRP.CRP(alpha)
        self.myu0 = 0
        self.dimension = 0
        self.data = []
        self.num = 0
        self.labels = []
        self.params = {}

    # クラスタリングするパターンを登録,初期化
    def input(self, data):
        self.data = data
        self.dimension = len(self.data[0])
        self.num = len(self.data)
        for _ in range(self.num):
            self.labels.append(0)
        #
        mx0 = sum(self.data[0])/self.num
        my0 = sum(self.data[1])/self.num
        
        mean0 = [mx0, my0]
        
        
    # 指定したラベルのパターンの平均と共分散行列を求める
    def getPartialParam(self, label):
        # 共分散行列を numpy で求める上で，データ形式は[[1次元目], [2次元目],...] ではなく [[1データ目], [2データ目], ...] の方がいい
        # → だから，やっぱりGMM_2d の出力はこの形にしよう
        x = []
        n = 0        
        for _ in range(self.dimension):
            x.append([])
        for i in range(self.num):
            if self.labels[i] == label:
                n = n + 1                
                for d in range(self.dimension):
                    x[d].append(self.data[d][i])
                #
            #
        #
        # 平均を求める
        mean = sum(x)/n
        # 共分散行列を求める
        sigma = np.cov(np.array(x).T)
        
        return [mean, sigma]        
        
        

    # 未知クラスタが選択された際の事後確率を求める．
    # 基底分布に正規ウィシャート分布を用いてパラメータθを積分消去したらこうなる（らしい）
    # 続パタ p.269 を参照のこと        
    def calcProbwithNewClass(self, x):
        Sb = np.linalg.inv(self.scale) + (self.beta/(1+self.beta))*(x-self.myu0)*(x-self.myu0).T
        coef = math.pow(self.beta/((1+self.beta)*math.pi) , self.dimension/2)
        t = math.pow(np.linalg.det(Sb), (self.df+1)/2) * math.gamma((self.df+1)/2)
        b = math.pow(np.linalg.det(self.scale), self.df/2) * math.gamma((self.df+1-self.dimension)/2)
        return coef*(t/b)

    # クラスラベルが推定された際のパラメータの最尤値（事後確率最大となる値）を求める
    # 続パタ p.269 の式 (12.37) を参考にした
    # 計算には以下を前提とした
    #   - 正規分布は平均で最大となる
    #   - 正規分布の平均の位置は分散（精度行列)に依らない
    #   - ウィシャート分布に関しても平均で最大となる
    def calcParamwithEstimatedLabel(self):
        print("まだ作ってないよ")        
        return 0





if __name__ == "__main__":
    print("Welcome to DPM_test")
    # クラスタリングを行うデータを生成
    c = 3
    means = [[0, 0], [-10, -10], [5, 10]]
    sigmas = [[[1, 0], [0, 1]], [[1, 0.5], [0.5, 1]], [[1, 0], [0, 2]]]
    rates = [0.3, 0.4, 0.3]
    size = 1000

    data = gmm.getData(c, means, sigmas, rates, size)
    print(data)

    # DPM を生成
    dpm = DPM()
    # パターンを登録

