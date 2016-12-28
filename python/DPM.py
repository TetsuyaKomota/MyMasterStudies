# -*- coding: utf-8 -*-
"""
Created on Wed Dec 28 13:59:17 2016

@author: komot
"""

import scipy.stats as ss
import numpy as np
import random.random
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
        # パラメータを初期化．平均，共分散ともに全データの平均と共分散
        self.params[0] = self.getPartialParam(0)
        # CRP も初期化
        self.crp.setInitCustomers(self.num)
        
    # ラベル指定．デバッグ用
    def setLabel(self, labels):
        if len(labels) == len(self.labels):
            self.labels = labels
            
        
        
    # 指定したラベルのパターンの平均と共分散行列を求める
    def getPartialParam(self, label):
        # 共分散行列を numpy で求める上で，データ形式は[[1次元目], [2次元目],...] ではなく [[1データ目], [2データ目], ...] の方がいい
        # → だから，やっぱりGMM_2d の出力はこの形にしよう
        x = []
        n = 0        
        for i in range(self.num):
            if self.labels[i] == label:
                n = n + 1                
                x.append(self.data[i])
            #
        #
        # 平均を求める
        mean = sum(x)/n
        # 共分散行列を求める
        sigma = np.cov(np.array(x).T)
        
        return [mean, sigma]        
        
        
    # 多次元正規分布から確率を求める．
    # 参考 http://emoson.hateblo.jp/entry/2015/02/06/182256    
    def mnd(_x, _mu, _sig):
        x = np.matrix(_x)
        mu = np.matrix(_mu)
        sig = np.matrix(_sig)
        a = np.sqrt(np.linalg.det(sig)*(2*np.pi)**sig.ndim)
        b = np.linalg.det(-0.5*(x-mu)*sig.I*(x-mu).T)
        return np.exp(b)/a

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
        
        
        
    # 学習の Sステップ
    # ギブスサンプリングによって現在のパラメータとパターンからラベルをサンプリング
    def stepS(self):
        for k in self.num:
            # CRP から k 番目の客を削除する
            self.crp.decline(self.labels[k])
            # 各クラスタと未知クラスタについて, k 番目のパターンの事後確率を求める
            p = {}
            for m in self.crp.customers.keys():
                p[m] = self.crp.getProbability(m)*self.mnd(self.data[k], self.params[m][0], self.params[m][1])
            #
            newlabel = self.crp.getNewLabel
            p[newlabel]=self.crp.getProbability(newlabel)*self.calcProbwithNewClass(self.data[k])
            # 正規化
            # しなくていいかもだけどしちゃダメな理由もないしな
            tempsum = sum(p.values())
            for i in p.keys():
                p[i] = p[i] / tempsum
            # サンプリング
            temp = 0
            rand = random()
            for m in p.keys():
                temp = temp + p[m]
                if rand < temp:
                    self.labels[k] = m
                    self.crp.addNewCustomer(m)
                    break
                #
            #
        #

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
    dpm.input(data)
    
    
    
    
