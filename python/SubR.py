# -*- coding: utf-8 -*-
"""
Created on Sat Jan  7 21:27:16 2017

@author: komot
"""

from CRP import CRP
import matplotlib.pyplot as plt

class SubR(CRP):
    '''
    crf   : 上位分布．下位分布で新テーブルのパラメータを取得する際にアクセスする
    alpha : 集中度
    params: 各テーブルのパラメータ
    '''
    def __init__(self, crf, alpha):
        CRP.__init__(self, alpha)
        self.crf = crf
        self.params = {}
        
    # テスト用．CRF でちゃんと SubR が生成できているか呼んでみただけ
    def call(self):
        print("This Restaurant's α :", end="")
        print(self.alpha)
        self.debug_show(26)
        
    # パターンの呼び出しのオーバーライド．
    # SubR ではテーブル番号ではなく，テーブルに配置された料理（パラメータ）を返す
    def getPattern(self):
        # CRP の getPattern() を使ってインデックスを取得
        label = super().getPattern()
        # 新しいテーブル番号（料理未配置）奈良 上位分布から新パラメータを取得
        if (label in self.params.keys()) == False:
            newparam = self.crf.getParamforNewTable()
            self.params[label] = newparam
        # パラメータを返す
        return self.params[label]
        
    # 客のデクリメントもオーバーライド．
    # テーブルがなくなった場合，そのテーブルの料理の客数を上位分布からデクリメントしなければならない
    # 個々の引数は インデックス指定なので注意
    def decline(self, idx):
        if idx in self.customers.keys():
            self.customers[idx] = self.customers[idx] - 1
            if self.customers[idx] <= 0:
                # 上位分布から，消えたテーブルが持っていた料理を探す
                param = self.params[idx]
                for i in range(len(self.crf.params)):
                    if param == self.crf.params[i]:
                        # 料理の客数をデクリメントする（上位分布の decline() を呼び出す）
                        self.crf.decline(i)
                        break
                # 下位分布のテーブルと料理を削除する
                del self.customers[idx]
                del self.params[idx]
                
    # 描画するよ
    def show(self, min=0, max=0, isSave="NON"):
        x= []
        for i in range(len(self.customers)):
            for t in range(self.customers[i]):
                x.append(self.params[i])
            #
        #
        if min >= max:
            plt.hist(x, bins=50)
        else:
            plt.hist(x, bins=50, range = (min, max))
        plt.show()
