# coding = utf-8

import numpy as np
from random import random
import matplotlib.pyplot as plt
import copy
import dill

class Kmeans:

    def __init__(self, K, D):
        self.k = K
        self.D = D
        self.mList = []
        for i in range(self.k):
            self.mList.append(np.array([random() for _ in range(D)]))
        self.mList = np.array(self.mList)


    def fit(self, X, detail=False):
        y = [int(self.k * random()) for _ in range(len(X))]

        count = 0
        while True:
            count += 1
            oldY = copy.deepcopy(y)
            # print(y)
            # E step
            for l in range(self.k):
                tempList = [X[i] for i in range(len(X)) if y[i]==l]
                if len(tempList) > 0:
                    self.mList[l] = sum(tempList)/len(tempList)
                else:
                    self.mList[l] = np.array([random() for _ in range(self.D)])

            # M step
            for i in range(len(X)):
                tempList = [self.distance(X[i], m) for m in self.mList]
                y[i] = tempList.index(min(tempList))
           
            if detail:
                print(len([i for i in range(len(y)) if y[i] != oldY[i]]))
                self.show(X)

            # Check
            e = len(y)/1000
            if len([i for i in range(len(y)) if y[i] != oldY[i]]) < e+count:
                break
 
        return y

    def predict(self, X, detail=False):
        if detail:
            self.show(X)
        y = [0 for _ in range(len(X))]
        for i in range(len(X)):
            tempList = [self.distance(X[i], m) for m in self.mList]
            y[i] = tempList.index(min(tempList))

        return y

    def show(self, X):
        size = int(len(X)/3)
        plt.scatter(X[:size, 0],    X[:size, 1], color="red")
        plt.scatter(X[size:size*2, 0], X[size:size*2, 1], color="blue")
        plt.scatter(X[size*2:, 0],    X[size*2:, 1], color="yellow")
        plt.scatter(self.mList[:, 0], self.mList[:, 1], color="black")
        plt.show() 
        
    # l1距離
    def _distance(self, x, y):
        return sum([abs(l) for l in list(x-y)])

    # l2距離
    def _distance(self, x, y):
        return np.linalg.norm(x-y)

    # l∞距離
    def _distance(self, x, y):
        return max([abs(l) for l in list(x-y)])

    # コサイン類似度
    def _distance(self, x, y):
        return 1-x.dot(y)/(np.linalg.norm(x)*np.linalg.norm(y))

    # 研究用
    def distance(self, x, y):
        size = int(len(x)/2)
        dist = 0
        for s in range(size):
            xs = x[s:s+2]
            ys = y[s:s+2]
            dist += 1 - xs.dot(ys)/(np.linalg.norm(xs)*np.linalg.norm(ys))
        return dist


    def saveModel(self, path):
        with open(path + "kmeans.dill", "wb") as f:
            dill.dump(self.mList, f)
 
    def loadModel(self, path):
        with open(path + "kmeans.dill", "rb") as f:
            self.mList = dill.load(f)
    
if __name__ == "__main__":

    size = 1000

    a = []

    temp = []
    temp.append(np.random.randn(size))
    temp.append(np.random.randn(size))
    temp = list(np.array(temp).T)

    a += temp

    temp = []
    temp.append(np.random.randn(size) + 3)
    temp.append(np.random.randn(size) + 3)
    temp = list(np.array(temp).T)

    a += temp

    temp = []
    temp.append(np.random.randn(size) + 6)
    temp.append(np.random.randn(size) + 6)
    temp = list(np.array(temp).T)

    a += temp

    a = np.array(a)

    print(a)
    plt.scatter(a[:size, 0],    a[:size, 1], color="red")
    plt.scatter(a[size:size*2, 0], a[size:size*2, 1], color="blue")
    plt.scatter(a[size*2:, 0],    a[size*2:, 1], color="yellow")
    plt.show() 
   
    model = Kmeans(3, 2) 
    model.fit(a, detail=True)
    print(model.predict(a, detail=True))
