#-*- coding: utf-8 -*-

import numpy as np
import scipy.stats as ss

DIMENSION = 2
NOIZE_X = 1.0 
NOIZE_V = 0.1 
NOIZE_A = 0.1 

class Maker:
    def __init__(self):
        self.timeStep = 0
        self.pdfX = ss.norm(scale = NOIZE_X)
        self.pdfV = ss.norm(scale = NOIZE_V)
        self.pdfA = ss.norm(scale = NOIZE_A)
        self.handX = np.zeros(DIMENSION)
        self.handV = np.zeros(DIMENSION)
        self.handA = np.zeros(DIMENSION)
        self.colorList = []
        self.colorList.append("red")
        self.colorList.append("blue")
        self.colorList.append("green")
        self.colorList.append("yellow")
        self.Xs = {}
        self.Vs = {}
        self.As = {}
        for c in self.colorList:
            self.Xs[c] = np.zeros(DIMENSION)
            self.Vs[c] = np.zeros(DIMENSION)
            self.As[c] = np.zeros(DIMENSION)
        self.f = open("tmp/log.csv", "a")

    # 色名から座標を取得
    def getXs(self, color):
        return self.Xs[color]

    # 色名から座標指定
    def setXs(self, color, xy):
        self.Xs[color] = np.array(xy)
        return self

    # 色名から座標移動
    def addXs(self, color, xy):
        self.Xs[color] = self.Xs[color] + np.array(xy)
        return self

    # 色名から速度を取得
    def getVs(self, color):
        return self.Vs[color]

    # 色名から速度指定
    def setVs(self, color, xy):
        self.Vs[color] = np.array(xy)
        return self

    # 色名から速度移動
    def addVs(self, color, xy):
        self.Vs[color] = self.Vs[color] + np.array(xy)
        return self

    # 色名から加速度を取得
    def getAs(self, color):
        return self.As[color]

    # 色名から座標指定
    def setAs(self, color, xy):
        self.As[color] = np.array(xy)
        return self

    # 色名から座標移動
    def addAs(self, color, xy):
        self.As[color] = self.As[color] + np.array(xy)
        return self

    # タイムステップ経過させる
    def nextStep(self):
        self.timeStep = self.timeStep + 1
        self.handX = self.handX + self.handV
        self.handV = self.handV + self.handA
        for c in self.colorList:
            self.Xs[c] = self.Xs[c] + self.Vs[c] + self.pdfX.rvs()
            self.Vs[c] = self.Vs[c] + self.As[c] + self.pdfV.rvs()

    # デバッグ用．現在の座標状況を取得する
    def debug_show(self):
        print("==SHOW== step:" + str(self.timeStep))
        status = ""
        status = status + "\t: " + str(self.handX)
        status = status + "\t: " + str(self.handV)
        status = status + "\t: " + str(self.handA)
        print("hand" + status)
        for i in range(len(self.colorList)):
            col = self.colorList[i]
            status = ""
            status = status + "\t: " + str(self.Xs[col])
            status = status + "\t: " + str(self.Vs[col])
            status = status + "\t: " + str(self.As[col])
            print(col + status)

    # デバッグ用．ログ出力
    def debug_log(self):
        # 出力の順番はステップ数，ハンド，colorList 順のオブジェクト
        # ハンドとオブジェクトはそれぞれ座標，速度，加速度
        self.f.write(str(self.timeStep) + ",")
        self.f.write(str(self.handX[0])+","+str(self.handX[1])+",")
        self.f.write(str(self.handV[0])+","+str(self.handV[1])+",")
        self.f.write(str(self.handA[0])+","+str(self.handA[1])+",")
        for c in self.colorList:
            self.f.write(str(self.Xs[c][0])+","+str(self.Xs[c][1])+",")
            self.f.write(str(self.Vs[c][0])+","+str(self.Vs[c][1])+",")
            self.f.write(str(self.As[c][0])+","+str(self.As[c][1])+",")
        self.f.write("\n")

if __name__ == "__main__":
    maker = Maker()
    maker.setVs("red", [2.0, 10.0])
    maker.setAs("red", [0, -1.0])
    for _ in range(100):
        maker.nextStep()
        maker.debug_show()
        maker.debug_log()
        if maker.getXs("red")[1] < 0:
            break 
