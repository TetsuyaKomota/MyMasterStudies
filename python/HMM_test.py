# -*- coding: utf-8 -*-
"""
Created on Wed Jan 18 13:56:15 2017

@author: komot
"""

import numpy as np
from hmmlearn import hmm
import scipy.stats as ss
import copy
import matplotlib.pyplot as plt

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

if __name__ == "__main__":
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
    
    model = hmm.GaussianHMM(n_components=3, covariance_type="full")    
    
    model.fit(datas[0:200])

    print("startprob_")
    print(model.startprob_)
    print("means_")
    print(model.means_)
    print("covars_")
    print(model.covars_)
    print("transmat_")
    print(model.transmat_)    
    
    for _ in range(10):
        sampleX, sampleZ = model.sample(100)
        sample = np.array(sampleX).T
        plt.plot(sample[0], sample[1])
    plt.show()
    