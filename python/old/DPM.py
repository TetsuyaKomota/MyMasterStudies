# -*- coding: utf-8 -*-
"""
Created on Wed Dec 28 13:59:17 2016

@author: komot
"""

'''

ディリクレ過程混合モデルの実装において，
ギブスサンプリングを用いたクラスラベルのサンプリング時に，未知クラスタに分類されるパターンが生じた直後に
そのクラスタのパラメータが推定されていない状態で次のパターンのラベルをサンプリングするとエラーが生じる問題がある．
その問題に関して，サンプリングを行う前にあらかじめ新規クラスラベルを一つに限定し，サンプリング直前に
存在していたクラスタ＋一つの新規クラスタのみからしかサンプリングされないという実装を行った．
結果，一つの新規クラスタに大半のデータが分類されてしまうという不具合が生じたため，
一つのラベルをサンプリングするごとにパラメータを更新するという方法で実装した v2 の作成を開始．
よってこっちのコードはもう使用しない

'''


import MyStatics as st
import scipy.stats as ss
import scipy.io
import numpy as np
from random import random
import GMMv2 as gmm
import CRP
import math

class DPM:
    def __init__(self, alpha=st.ALPHA, beta=st.BETA, df=st.DF, scale=st.SCALE):
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
        # Sステップで変更があったクラスにチェックし，Mステップではそのクラスだけ計算するためのフラグ
        self.flags = {}
        # 最尤度
        self.score = 0
        # 最尤ラベル
        self.likelylabels = []
        # 非更新回数
        self.iter_non = 0
        # 停止フラグ.Vステップで操作する
        self.stop_flag = False

    # クラスタリングするパターンを登録,初期化
    def input(self, data):
        self.data = data
        self.dimension = len(self.data[0])
        self.num = len(self.data)
        for _ in range(self.num):
            self.labels.append(0)
            self.likelylabels.append(0)
        #
        # パラメータを初期化．平均，共分散ともに全データの平均と共分散
        self.params[0] = self.getPartialParam(0)
        self.myu0 = self.params[0][0]
        # CRP も初期化
        self.crp.setInitCustomers(self.num)
        # デバッグ用
        self.debug_show(53)
        
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
    def mnd(self, data, myu, sigma):
        x = np.matrix(data)
        mu = np.matrix(myu)
        sig = np.matrix(sigma)
        a = np.sqrt(np.linalg.det(sig)*(2*np.pi)**sig.ndim)
        b = np.linalg.det(-0.5*(x-mu)*sig.I*(x-mu).T)
        return np.exp(b)/a

    # 未知クラスタが選択された際の事後確率を求める．
    # 基底分布に正規ウィシャート分布を用いてパラメータθを積分消去したらこうなる（らしい）
    # 続パタ p.269 を参照のこと        
    # *************************************************************************
    # *************************************************************************
    # 動作確認したところ，どうやらこれが見当違いな値を出しているっぽい．
    # 本当に教科書通りにできているか，教科書の式の解釈がそもそもあっているかの２通りで検証
    # *************************************************************************
    # *************************************************************************
    def calcProbwithNewClass(self, x):
        Sb = np.linalg.inv(np.linalg.inv(self.scale) + (self.beta/(1+self.beta))*(x-self.myu0)*((x-self.myu0).T))
        coef = math.pow(self.beta/((1+self.beta)*math.pi) , self.dimension/2)
        t = math.pow(np.linalg.det(Sb), (self.df+1)/2) * math.gamma((self.df+1)/2)
        b = math.pow(np.linalg.det(self.scale), self.df/2) * math.gamma((self.df+1-self.dimension)/2)
        # デバッグ
        '''
        print("debug dimension :", end="")
        print(self.dimension)
        print("debug df :", end="")
        print(self.df)
        print("debug S :", end="")
        print(self.scale)
        print("debug det(S) :", end="")
        print(np.linalg.det(self.scale))
        print("debug Sb :", end="")
        print(Sb)
        print("debug det(Sb) :", end="")
        print(np.linalg.det(Sb))
        print("debug coef :", end="")
        print(coef)
        print("debug t :", end="")
        print(t)
        print("debug b :", end="")
        print(b)
        '''
        return coef*(t/b)

    # クラスラベルが推定された際のパラメータの最尤値（事後確率最大となる値）を求める
    # 続パタ p.269 の式 (12.37) を参考にした
    # 計算には以下を前提とした
    #   - 正規分布は平均で最大となる
    #   - 正規分布の平均の位置は分散（精度行列)に依らない
    #   - ウィシャート分布に関しても平均で最大となる
    def calcParamwithEstimatedLabel(self, label):
        # 指定クラスタに所属するパターンの数を数える
        ni = 0
        x_mean = 0 
        for i in range(self.num):
            if self.labels[i] == label:
                ni = ni+1
                x_mean = x_mean + self.data[i]
            #
        #
        # サンプリングの結果客がいなくなったクラスタのパラメータは削除し，削除信号を返す
        if ni == 0:
            if label in self.params.keys():
                del self.params[label]
            return ["DELETED"]
        
        x_mean = x_mean / ni
        #諸々計算
        # 正規分布の平均は分散に依らないとすると μi = μc
        myu = (ni*x_mean + self.beta*self.myu0)/(ni + self.beta)
        # ウィシャート分布の最大は平均に等しいとすると，続パタ付録より Λ = df*scale
        lamda = self.df * self.scale
        sigma = np.linalg.inv(lamda)
    
        return [myu, sigma]
        
        
        
    # 学習の Sステップ
    # ギブスサンプリングによって現在のパラメータとパターンからラベルをサンプリング
    def stepS(self):
        # フラグの初期化
        for m in self.crp.customers.keys():
            self.flags[m] = False
        #サンプリング前のクラスタの種類と未知クラスタラベルを取得しておく
        # サンプリングの過程で新たなクラスタが生じた場合，Mステップでパラメータを取得する前に次のパターンのサンプリングを行うとエラーになる
        # その解決方法として，一度のSステップでは新クラスタは1種類のみとするか，パターンごとのサンプリングのたびにパラメータ更新するか
        # 今回は前者で実装することにしたが，どっちが正解かはわからない
        curkind = []
        for m in self.crp.customers.keys():
            curkind.append(m)
        curnew =self.crp.getNewLabel()
        # デバッグ
        print("debug curnew :", end="")
        print(curnew)
        for k in range(self.num):
            # CRP から k 番目の客を削除する
            before = self.labels[k]
            self.crp.decline(self.labels[k])
            # 各クラスタと未知クラスタについて, k 番目のパターンの事後確率を求める
            p = {}
            # for m in self.crp.customers.keys():
            # デバッグ用
            '''            
            self.crp.debug_show(183)
            print("curkind:",end="")
            print(curkind)
            '''
            for m in curkind:
                #サンプリングの過程でなくなったクラスタは考慮しない
                if m in self.crp.customers.keys():
                    p[m] = self.crp.getProbability(m)*self.mnd(self.data[k], self.params[m][0], self.params[m][1])
                #
            #
            # newlabel = self.crp.getNewLabel()
            # p[newlabel]=self.crp.getProbability(newlabel)*self.calcProbwithNewClass(self.data[k])
            p[curnew]=self.crp.getProbability(curnew)*self.calcProbwithNewClass(self.data[k])
            # 正規化
            # しなくていいかもだけどしちゃダメな理由もないしな
            tempsum = sum(p.values())
            for i in p.keys():
                p[i] = p[i] / tempsum
            # デバッグ．p を表示
            print("debug p=",end="")
            print(p)
            # サンプリング
            temp = 0
            rand = random()
            for m in p.keys():
                temp = temp + p[m]
                if rand < temp:
                    self.labels[k] = m
                    # クラスラベルが変化したら，フラグを立てる
                    if before != m:
                        self.flags[before] = True
                        self.flags[m] = True
                    self.crp.addNewCustomer(m)
                    break
                #
            #
        #
        # デバッグ用．サンプリング結果を表示する
        # self.debug_show(167)
                    
    # 学習の Mステップ
    # Sステップによってサンプリングしたクラスラベルをもとにパラメータを更新する
    def stepM(self):
        for m in self.flags.keys():
            if self.flags[m] == True:
                newparams = self.calcParamwithEstimatedLabel(m)
                # すでに消滅しているクラスタの場合，パラメータの更新は行わない
                if newparams[0] != "DELETED":
                    self.params[m] = newparams
            #
        #

    # 学習の Vステップ
    #尤度を計算する．終了判定もここで行う
    def stepV(self):
        curscore = 1
        for k in range(self.num):
            curscore = curscore + math.log(self.mnd(self.data[k], self.params[self.labels[k]][0], self.params[self.labels[k]][1]))
        #
        if curscore > self.score:
            self.score = curscore
            self.likelylabels = self.labels
            self.iter_non = 0
        else:
            self.labels = self.likelylabels
            self.iter_non = self.iter_non + 1
            if self.iter_non > st.MAX_ITER_NON:
                self.stop_flag = True
            #
        #
        
        
    # 内部変数表示．デバッグ用
    def debug_show(self, idx):
        print("debug for DPM idx="+str(idx)+" : ")
        # print("data : ", end="")
        # print(self.data)
        print("labels : ",end="")
        print(self.labels)
        print("params : ")
        for p in self.params:
            print("Cluster:"+str(p))
            print("coef   :"+str(self.crp.getProbability(p)))
            print("myu    :"+str(self.params[p][0]))
            print("sigma  :")
            print(self.params[p][1])

if __name__ == "__main__":
    print("Welcome to DPM_test")
    # クラスタリングを行うデータを生成
    """
    c = 3
    means = [[0, 0], [-10, -10], [5, 10]]
    sigmas = [[[1, 0], [0, 1]], [[1, 0.5], [0.5, 1]], [[1, 0], [0, 2]]]
    rates = [0.3, 0.4, 0.3]
    size = 1000

    data = gmm.getData(c, means, sigmas, rates, size)
    """
    data = scipy.io.loadmat("Inputdata.mat")["Inputsample"]
    print(data)
    # exit()

    # DPM を生成
    dpm = DPM()
    # パターンを登録
    dpm.input(data)
    # 学習開始
    n_iter = 0
    while(dpm.stop_flag == False):
        n_iter = n_iter + 1
        print("ITERATION : " + str(n_iter))
        dpm.stepS()
        dpm.stepM()
        dpm.stepV()
        dpm.debug_show(317)
    # 学習結果を表示
    print("ほげほげ")
    with open("results4Woung.txt", "w", encoding="utf-8") as f:
        f.write("labels:\n")
        f.write(str(dpm.labels)+"\n") 
        f.write("params:\n")
        for p in dpm.params:
            f.write("Cluster:"+str(p)+"\n")
            f.write("coef   :"+str(dpm.crp.getProbability(p))+"\n")
            f.write("myu    :"+str(dpm.params[p][0])+"\n")
            f.write("sigma  :"+"\n")
            f.write(str(dpm.params[p][1])+"\n")

       
    
