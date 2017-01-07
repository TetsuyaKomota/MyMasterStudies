# -*- coding: utf-8 -*-
"""
Created on Sat Jan  7 21:26:25 2017

@author: komot
"""

'''
中華料理店フランチャイズ
'''
import SubR

class CRF:
    '''
    gamma : 上位分布の集中度 γ
    alpha : 下位分布の集中度 α
    numofR: 店数 (多分データ数)
    '''
    def __init__(self, gamma, alpha, numofR):
        self.gamma = gamma
        self.alpha = alpha
        self.subRs = []
        for i in range(numofR):
            self.subRs.append(SubR.SubR(self.alpha))
            
    # テスト用．すべての店の call を呼ぶだけ
    def chorus(self):
        for i in range(len(self.subRs)):
            print("from Sub Restaurant no.%d  :: " % i, end="")
            self.subRs[i].call()
            
            
if __name__ == "__main__":
    gamma = 0.1    
    alpha = 1.0
    num = 5
    
    crf = CRF(gamma, alpha, num)
    
    crf.chorus()