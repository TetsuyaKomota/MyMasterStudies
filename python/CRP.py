# -*- coding: utf-8 -*-
"""
Created on Mon Dec 26 22:36:10 2016

@author: tetsuya
"""

import numpy as np
import matplotlib.pyplot as plt

class CRP:
    def __init__(self, alpha):
        self.alpha = alpha
        self.customers = {}

    # 初期化．指定した人数を一つのクラスに入れる        
    def setInitCustomers(self, size):
        self.customers[0] = size

    def getNumofCustomers(self):
        output = 0
        for i in self.customers:
            output = output + self.customers[i]
        return output
        
    def getNewLabel(self):
        idx = 0
        while True:
            if idx in self.customers.keys():
                idx = idx + 1
            else:
                break
        return idx

    def getProbability(self, label):
        n = self.getNumofCustomers()
        if label in self.customers.keys():
            return self.customers[label]/(n+self.alpha)
        else:
            return self.alpha/(n+self.alpha)
    
    def addNewCustomer(self, label):
        if label in self.customers.keys():
            self.customers[label] = self.customers[label]+1
        else:
            self.customers[label] = 1

    def getPattern(self):
        output = -1
        rand = np.random.random()
        tempsum = 0
        for i in self.customers.keys():
            tempsum = tempsum + self.getProbability(i)
            if rand < tempsum:
                output = i
                break
            #
        #
        if output == -1:
            output = self.getNewLabel()
        self.addNewCustomer(output)
        return output
    
    def decline(self, idx):
        if idx in self.customers.keys():
            self.customers[idx] = self.customers[idx] - 1
            if self.customers[idx] == 0:
                del self.customers[idx]
        
if __name__ == "__main__":
    crp = CRP(5)
    x = []
    for _ in range(10000):
        x.append(crp.getPattern())
    #
    plt.hist(x, bins = 50)
    plt.show()
    