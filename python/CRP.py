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

    def getPattern(self):
        output = -1
        rand = np.random.random()
        n = self.getNumofCustomers()
        tempsum = 0
        for i in self.customers:
            tempsum = tempsum + (self.customers[i]/(n+self.alpha))
            if rand < tempsum:
                output = i
                break
            #
        #
        if output == -1:
            output = self.getNewLabel()
            self.customers[output] = 1
        else:
            self.customers[output] = self.customers[output] + 1
        return output
    
    def decline(self, idx):
        if idx in self.customers.keys():
            self.customers[idx] = self.customers[idx] - 1
            if self.customers[idx] == 0:
                del self.customers[idx]
        
if __name__ == "__main__":
    crp = CRP(100)
    x = []
    for _ in range(10000):
        x.append(crp.getPattern())
    #
    plt.hist(x, bins = 100)
    plt.show()
    