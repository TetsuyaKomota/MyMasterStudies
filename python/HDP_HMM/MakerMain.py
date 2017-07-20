#-*- coding: utf-8 -*-

import numpy as np
import scipy.stats as ss
from datetime import datetime

DIMENSION = 2
NOIZE_X = 0.1 
NOIZE_V = 0.0 
NOIZE_A = 0.0 
# grab の可能範囲
GRAB_RANGE = 1000000
# 速度減衰強度
REDIS_V = 0.9

class Maker:
    def __init__(self, filename=str(datetime.now().timestamp())[-5:]):
        self.timeStep = 0
        self.grabbed = ""
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
        self.f = open("../tmp/log_MakerMain/log" + filename + ".csv", "a")

    # 色名から座標を取得
    def getXs(self, color):
        if color == "hand":
            return self.handX
        else:
            return self.Xs[color]

    # 色名から座標指定
    def setXs(self, color, xy):
        if color == "hand":
            self.handX = np.array(xy)
            if self.grabbed != "":
                self.setXs(self.grabbed, xy)
        else:
            self.Xs[color] = np.array(xy)
        return self

    # 色名から座標移動
    def addXs(self, color, xy):
        if color == "hand":
            self.handX = self.handX + np.array(xy)
            if self.grabbed != "":
                self.addXs(self.grabbed, xy)
        else:
            self.Xs[color] = self.Xs[color] + np.array(xy)
        return self

    # 色名から速度を取得
    def getVs(self, color):
        if color == "hand":
            return self.handV
        else:
            return self.Vs[color]

    # 色名から速度指定
    def setVs(self, color, xy):
        if color == "hand":
            self.handV = np.array(xy)
            if self.grabbed != "":
                self.setVs(self.grabbed, xy)
        else:
            self.Vs[color] = np.array(xy)
        return self

    # 色名から速度移動
    def addVs(self, color, xy):
        if color == "hand":
            self.handV = self.handV + np.array(xy)
            if self.grabbed != "":
                self.addVs(self.grabbed, xy)
        else:
            self.Vs[color] = self.Vs[color] + np.array(xy)
        return self

    # 色名から加速度を取得
    def getAs(self, color):
        if color == "hand":
            return self.handA
        else:
            return self.As[color]

    # 色名から加速度指定
    def setAs(self, color, xy):
        if color == "hand":
            self.handA = np.array(xy)
            if self.grabbed != "":
                self.setAs(self.grabbed, xy)
        else:
            self.As[color] = np.array(xy)
        return self

    # 色名から加速度移動
    def addAs(self, color, xy):
        if color == "hand":
            self.handA = self.handA + np.array(xy)
            if self.grabbed != "":
                self.addAs(self.grabbed, xy)
        else:
            self.As[color] = self.As[color] + np.array(xy)
        return self

    # 色名，目標地点から，目標地点に減衰しながらまっすぐ向かうように
    # 速度と加速度を変更
    # t は到達までのステップ数
    def gotoGoal(self, color, goal, t):
        dis = np.array(goal)-self.getXs(color)
        self.setVs(color, 2*dis/t)
        self.setAs(color, -2*dis/(t*t))

    # 色名，目標地点から，目標地点に円弧を描いて向かう
    # 加速度が変化しながら動くので execute 要素を含む
    def executeCircle(self, color, goal, t):
        self.setVs(color, [0, 0])
        self.setAs(color, [0, 0])
        base = (self.getXs(color) + np.array(goal))/2
        dis = np.linalg.norm(np.array(goal) - self.getXs(color))/2
        # dis = dis * (np.pi/t) * (np.pi/t)
        for d in range(t):
            diff = [dis*np.cos(np.pi*d/t), dis*np.sin(np.pi*d/t)]
            self.setXs(color, base+np.array(diff))
            self.nextStep()
            self.debug_show()
            self.debug_log()
            

    # 色指定で握る
    def grab(self, color):
        if self.grabbed != "":
            print("hand already grabbed:" + self.grabbed)
        elif np.linalg.norm(self.getXs("hand")-self.getXs(color)) < GRAB_RANGE:
            self.grabbed = color
            self.setVs(color, self.getVs("hand"))
            self.setAs(color, self.getAs("hand"))
        else:
            print("too far")

    # 色指定で離す
    def release(self):
        if self.grabbed == "":
            print("nothing grabbed")
        else:
            self.setAs(self.grabbed, np.zeros(DIMENSION))
            self.grabbed = ""

    # ノイズを作る
    def genNoize(self, unit):
        output = np.zeros(DIMENSION)
        if unit == "X":
            pdf = self.pdfX
        elif unit == "V":
            pdf = self.pdfV
        else:
            pdf = self.pdfA
        for d in range(DIMENSION):
            output[d] = pdf.rvs()
        return output
 
    # タイムステップ経過させる
    def nextStep(self):
        self.timeStep = self.timeStep + 1
        self.handX = self.handX + self.handV + self.genNoize("X")
        self.handV = self.handV + self.handA + self.genNoize("V")
        if np.linalg.norm(self.handA) < 0.1 :
            self.handV = self.handV * REDIS_V
            if np.linalg.norm(self.handV) < 0.1 :
                self.handV = np.zeros(DIMENSION)
        for c in self.colorList:
            self.Xs[c] = self.Xs[c] + self.Vs[c] + self.genNoize("X")
            self.Vs[c] = self.Vs[c] + self.As[c] + self.genNoize("V")
            if np.linalg.norm(self.As[c]) < 0.1 :
                self.Vs[c] = self.Vs[c] * REDIS_V
                if np.linalg.norm(self.Vs[c]) < 0.1 :
                    self.Vs[c] = np.zeros(DIMENSION)

    # 指定した回数タイムステップを進ませてログをとる
    def execute(self, num):
        for _ in range(num):
            self.nextStep()
            self.debug_show()
            self.debug_log()
 
 
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
    maker.setVs("hand", [2.0, 10.0])
    maker.setAs("hand", [0, -1.0])
    maker.setXs("red", [20.0, 53.0])
    for _ in range(100):
        maker.nextStep()
        maker.debug_show()
        maker.debug_log()
        if maker.getXs("hand")[1] < 0:
            break 
        elif maker.getVs("hand")[1] <=0:
            maker.setVs("red", maker.getVs("hand"))
            maker.setAs("red", maker.getAs("hand"))
