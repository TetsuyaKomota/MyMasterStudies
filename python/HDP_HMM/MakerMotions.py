import HDP_HMM.MakerMain as makerMain
import numpy as np
from random import random

def test1(maker, inits):
    # 初期化
    maker.setXs("hand", [1000, 1000])
    maker.setXs("red", [10000, 1000])
    maker.setXs("blue", [-2000, 10000])
    # 二つの物体を中心に移動する
    # 赤の方に手を伸ばす
    # maker.setVs("hand", [180, 0])
    # maker.setAs("hand", [-1.8, 0])
    maker.gotoGoal("hand", maker.getXs("red"), 100)
    """
    while(True):
        maker.nextStep()
        maker.debug_show()
        maker.debug_log()
        if np.linalg.norm(maker.getVs("hand")) < 10:
            maker.grab("red")
            # maker.addVs("hand", [0, 100])
            # maker.setAs("hand", [0, 0])
            maker.gotoGoal("hand", [0, 0], 100)
            break
    """
    maker.execute(100)
    maker.grab("red")
    maker.gotoGoal("hand", [0, 0], 100)
    maker.execute(100)
    maker.release()
    maker.gotoGoal("hand", maker.getXs("blue"), 100)
    maker.execute(100)
    maker.grab("blue")
    maker.gotoGoal("hand", [0, 0], 100)
    maker.execute(100)
    maker.setXs("hand", [0, 0])
    maker.executeCurve("hand", [10000, 0], 200)

def test2(maker, inits):
    # 初期化
    maker.setXs("hand"  , [0, 0])
    maker.setXs("red"   , inits["red"])
    maker.setXs("blue"  , inits["blue"])
    maker.setXs("yellow", inits["yellow"])
    maker.setXs("green" , inits["green"])

    # 0.
    maker.gotoGoal("hand", (maker.getXs("hand") + 99*maker.getXs("red"))/100, 100)
    maker.execute(100)
    maker.grab("red")
    # 1.
    maker.gotoGoal("hand", (maker.getXs("hand") + 5*maker.getXs("yellow"))/6, 100)
    maker.execute(100)
    maker.release()
    # 2.
    maker.gotoGoal("hand", (maker.getXs("hand") + 99*maker.getXs("blue"))/100, 100)
    maker.execute(100)
    maker.grab("blue")
    # 3.
    maker.gotoGoal("hand", (2*maker.getXs("yellow") - maker.getXs("red")), 100)
    maker.execute(100)
    maker.release()
    # 4.    
    maker.gotoGoal("hand", [0, 0], 100)
    maker.execute(100)

def test2_1(maker, inits):
    # test2 と同じ動作だが，最終位置は比でなく絶対値で配置する
    # 初期化
    maker.setXs("hand"  , [0, 0])
    maker.setXs("red"   , inits["red"])
    maker.setXs("blue"  , inits["blue"])
    maker.setXs("yellow", inits["yellow"])
    maker.setXs("green" , inits["green"])

    # 0.
    dist = maker.getXs("hand") - maker.getXs("red")
    maker.gotoGoal("hand", maker.getXs("red") + dist/np.linalg.norm(dist) * 5, 100)
    maker.execute(100)
    maker.grab("red")
    # 1.
    dist = maker.getXs("hand") - maker.getXs("yellow")
    maker.gotoGoal("hand", maker.getXs("yellow") + dist/np.linalg.norm(dist) * 30, 100)
    maker.execute(100)
    maker.release()
    # 2.
    dist = maker.getXs("hand") - maker.getXs("blue")
    maker.gotoGoal("hand", maker.getXs("blue") + dist/np.linalg.norm(dist) * 5, 100)
    maker.execute(100)
    maker.grab("blue")
    # 3.
    maker.gotoGoal("hand", (2*maker.getXs("yellow") - maker.getXs("red")), 100)
    maker.execute(100)
    maker.release()
    # 4.    
    maker.gotoGoal("hand", [0, 0], 100)
    maker.execute(100)

def test3(maker, inits, num=0):
    # 初期化
    maker.setXs("hand"  , [0, 0])
    maker.setXs("red"   , inits["red"])
    maker.setXs("blue"  , inits["blue"])
    maker.setXs("yellow", inits["yellow"])
    maker.setXs("green" , inits["green"])

    # 0.
    maker.gotoGoal("hand", maker.getXs("red"), 100)
    maker.execute(50)
    if num == 0:
        maker.executeCircle("hand", 100)
    maker.execute(50)
    maker.grab("red")
    # お試し
    # 1.
    maker.gotoGoal("hand", (maker.getXs("hand") + 9*maker.getXs("yellow"))/10, 100)
    rand = int(100*random())
    maker.execute(rand)
    if num == 1:
        maker.executeCircle("hand", 100)
    maker.execute(100-rand)
    maker.release()
    # 2.
    maker.gotoGoal("hand", maker.getXs("blue"), 100)
    rand = int(100*random())
    maker.execute(rand)
    if num == 2:
        maker.executeCircle("hand", 100)
    maker.execute(100-rand)
    maker.grab("blue")
    # 3.
    maker.gotoGoal("hand", (2*maker.getXs("yellow") - maker.getXs("red")), 100)
    rand = int(100*random())
    maker.execute(rand)
    if num == 3:
        maker.executeCircle("hand", 100)
    maker.execute(100-rand)
    maker.release()
    # 4.    
    maker.gotoGoal("hand", [0, 0], 100)
    rand = int(100*random())
    maker.execute(rand)
    if num == 4:
        maker.executeCircle("hand", 100)
    maker.execute(100-rand)

# 初期状態を適当に作る
def getInits():
    inits = {}
    inits["red"]    = [10000 * (random() - 0.5), 10000 * (random() - 0.5)]
    inits["blue"]   = [10000 * (random() - 0.5), 10000 * (random() - 0.5)]
    inits["yellow"] = [10000 * (random() - 0.5), 10000 * (random() - 0.5)]
    inits["green"]  = [10000 * (random() - 0.5), 10000 * (random() - 0.5)]
    return inits

def execute(testNumber, isShuffleInits, numofData, detail=False):
    if testNumber == 1:
        testMethod = test1
    elif testNumber == 2:
        testMethod = test2
    elif testNumber == 21:
        testMethod = test2_1
    elif testNumber == 3:
        testMethod = test3
    else:
        if detail == True:
            print("[MakerMotions]execute:invalid testNumber:", end="")
            peinr(str(testNumber))
        return 
    inits = getInits()
    for i in range(numofData):
        if isShuffleInits == True:
            inits = getInits()
        filename = "000000"+"{0:03d}".format(i)
        maker = makerMain.Maker(filename)
        testMethod(maker, inits)

if __name__ == "__main__":
    """
    maker = makerMain.Maker()
    maker.debug_show()
    test1(maker)
    exit()
    """
    for count in range(10):
        inits = {}
        inits["red"]    = [10000 * (random() - 0.5), 10000 * (random() - 0.5)]
        inits["blue"]   = [10000 * (random() - 0.5), 10000 * (random() - 0.5)]
        inits["yellow"] = [10000 * (random() - 0.5), 10000 * (random() - 0.5)]
        inits["green"]  = [10000 * (random() - 0.5), 10000 * (random() - 0.5)]
        for i in range(10):
            filename = "000"+"{0:03d}".format(count)+"{0:03d}".format(i)
            maker = makerMain.Maker(filename)
            maker.debug_show()
            test2(maker, inits)
    """
    for interval in range(5):
        for count in range(10):
            inits = {}
            inits["red"]    = [10000 * (random() - 0.5), 10000 * (random() - 0.5)]
            inits["blue"]   = [10000 * (random() - 0.5), 10000 * (random() - 0.5)]
            inits["yellow"] = [10000 * (random() - 0.5), 10000 * (random() - 0.5)]
            inits["green"]  = [10000 * (random() - 0.5), 10000 * (random() - 0.5)]
            for i in range(5):
                filename = "1"+str(interval)+"0"+"{0:03d}".format(count)+"{0:03d}".format(i)
                maker = makerMain.Maker(filename)
                maker.debug_show()
                test3(maker, inits, num = interval)

    """
