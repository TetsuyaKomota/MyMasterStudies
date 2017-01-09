# -*- coding: utf-8 -*-
"""
Created on Sat Jan  7 21:26:25 2017

@author: komot
"""

'''
中華料理店フランチャイズ
'''
import SubR
from CRP import CRP
import scipy.stats as ss

import matplotlib.pyplot as plt

class CRF(CRP):
    '''
    H     : 基底測度. scipy.stats で定義すること
    gamma : 上位分布の集中度 γ
    alpha : 下位分布の集中度 α
    numofR: 店数 (多分データ数)
    '''
    def __init__(self, H, gamma, alpha, numofR):
        CRP.__init__(self, alpha)        
        self.H = H        
        self.gamma = gamma
        self.alpha = alpha
        '''
        params : 上位分布（このクラス）の既存のパラメータ（料理）.キーは customers の物と一致させる
        subRs  : 下位分布（各店）．多分配列で問題ない
        '''
        self.params = {}
        self.subRs = []
        for i in range(numofR):
            # SubR のインスタンス生成の引数に self が入ってるのはミスじゃなくて親の参照を渡してるだけだから注意
            self.subRs.append(SubR.SubR(self, self.alpha))
            
    # テスト用．すべての店の call を呼ぶだけ
    def chorus(self):
        for i in range(len(self.subRs)):
            print("from Sub Restaurant no.%d  :: " % i, end="")
            self.subRs[i].call()
    
    # 下位分布に対して新パラメータを提供する
    def getParamforNewTable(self):
        # 上位分布の CRP に従ってパラメータのインデックスを取得
        label = self.getPattern()
        # 新しいインデックスなら客数をインクリメントしてパラメータを返す
        # → getPattern() の時点で客数はインクリメントされてたから，こっちでインクリメント処理はいらない
        if (label in self.params.keys()) == False:
            # scipy.stats によって H が定義されていれば rvs を持つはず
            newparam = self.H.rvs()
            self.params[label] = newparam
        return self.params[label]
        
    # ここの感じ汚いなぁ...
    # 下位分布でテーブルが消滅した際，そのテーブルに乗っていた料理の客数を上位分布からデクリメントする
    # 料理が消滅するときの処理が CRP まんまの実装とは違うから SubR からコピペでオーバーライド
    def decline(self, idx):
        if idx in self.customers.keys():
            self.customers[idx] = self.customers[idx] - 1
            if self.customers[idx] <= 0:
                # 下位分布のテーブルと料理を削除する
                del self.customers[idx]
                # これのためだけにオーバーライド...  CRP を作り直した方が美しいな
                del self.params[idx]
                
    # 中身の表示．デバッグ用
    # これも結局 SubR とまんま一緒なんだよな．ゼミ終わったらこの辺書き直そう
    def show(self, isSave="NON"):
        min = 0
        max = 0
        x= []
        for i in range(len(self.customers)):
            if min == 0 and max == 0:
                min = self.params[i]
                max = self.params[i]
            elif min > self.params[i]:
                min = self.params[i]
            elif max < self.params[i]:
                max = self.params[i]
            for t in range(self.customers[i]):
                x.append(self.params[i])
            #
        #
        print("Base measure")
        plt.hist(self.H.rvs(100000), bins=50)
        plt.show()

        print("Super distribution")                
        if min >= max:
            plt.hist(x, bins=50)
        else:
            plt.hist(x, bins=50, range = (min, max))
        plt.show()
        
        print("Sub distribution")
        for r in self.subRs:
            r.show(min=min, max=max)

                    
            
            
if __name__ == "__main__":
    H = ss.norm(loc = 0, scale = 1)
    gamma = 1    
    alpha = 5
    num = 5
    
    crf = CRF(H, gamma, alpha, num)
    
    crf.chorus()
    
    for _ in range(10000):
        for r in crf.subRs:
            print("pick : ", end="")
            print(r.getPattern())
    crf.show()