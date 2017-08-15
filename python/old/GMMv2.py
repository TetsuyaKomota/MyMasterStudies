# -*- coding: utf-8 -*-
"""
Created on Wed Dec 28 16:29:22 2016

@author: komot
"""

#-*- coding:utf-8 -*-

# http://www.sas.com/offices/asiapacific/japan/service/technical/faq/list/body/stat034.html

import numpy as np
import matplotlib.pyplot as plt
from time import sleep

def getData(c, means, sigmas, rates, size):

    output = []

    # クラスタ数 c と 平均、分散、混合比の数が一致してなければエラー
    if c != len(means) or c != len(sigmas) or c != len(rates):
        print("ERROR: invalid inputs")
        return output

    for i in range(c):
        # 混合比に応じた量のデータを生成
        n = int(size*rates[i])
        # 準備
        a = sigmas[i][0][1]/(sigmas[i][0][0])
        b = np.sqrt(sigmas[i][1][1] - ((sigmas[i][0][1]*sigmas[i][0][1])/sigmas[i][0][0]))
        
        # 乱数生成
        for k in range(n):
            x = (means[i][0] + np.sqrt(sigmas[i][0][0]) * np.random.randn())
            y = (means[i][1] + a * (x - means[i][0]) + b * np.random.randn())
            output.append(np.array([x, y]))
        #
    #
    return output

if __name__ == "__main__":
    c = 3
    means = [[0, 0], [-10, -10], [5, 10]]
    sigmas = [[[1, 0], [0, 1]], [[1, 0.5], [0.5, 1]], [[1, 0], [0, 2]]]
    rates = [0.3, 0.4, 0.3]
    size = 100

    fdata = getData(c, means, sigmas, rates, size)

    print(fdata)

    # 描画しよう
    # 描画用にデータを整理
    
    data = [[], []]
    for i in range(len(fdata)):
        data[0].append(fdata[i][0])
        data[1].append(fdata[i][1])

    pi = 0
    for i in range(c):
        n = int(size*rates[i])
        print(n)
        plt.scatter(data[0][pi:pi+n], data[1][pi:pi+n], s=20+10*i,color = [(np.sqrt(2)*i)%1, (np.sqrt(3)*i)%1, (np.sqrt(5)*i)%1],  label=str(i))
        pi = pi + n


    plt.grid(True)

    plt.legend(loc='upper left')
    plt.show()
    sleep(3)
