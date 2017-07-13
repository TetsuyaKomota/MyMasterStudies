#-*- coding: utf-8 -*-

"""
とりあえず設定だけ決めていこう
・空間には物体が4つとハンドの5つ
・2次元
・
"""
import numpy as np

DIMENSION = 2

class Maker:
    def __init__(self):
        self.timeStep = 0
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
            self.Xs[c] = self.Xs[c] + self.Vs[c]
            self.Vs[c] = self.Vs[c] + self.As[c]

    # デバッグ用．現在の座標状況を取得する
    def debug_show(self):
        print("==SHOW==")
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

if __name__ == "__main__":
    maker = Maker()
    """
    # maker.debug_show()
    maker.setXs("red", [1.0, 2.0])
    maker.debug_show()
    maker.addXs("red", [1.0, 1.0])
    maker.debug_show()
    """
    maker.setVs("red", [10.0, 0])
    maker.setAs("red", [-1.0, 0])
    for _ in range(100):
        maker.nextStep()
        maker.debug_show()
        if maker.getVs("red")[0] <= 0:
            break 
