import MakerMain
import numpy as np
from random import random

def test1(maker):
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
    maker.executeCircle("hand", [10000, 0], 200)

def test2(maker, inits):
    # 初期化
    maker.setXs("hand"  , [0, 0])
    maker.setXs("red"   , inits["red"])
    maker.setXs("blue"  , inits["blue"])
    maker.setXs("yellow", inits["yellow"])
    maker.setXs("green" , inits["green"])

    # 0.
    maker.gotoGoal("hand", maker.getXs("red"), 100)
    maker.execute(100)
    maker.grab("red")
    # 1.
    maker.gotoGoal("hand", (maker.getXs("hand") + 9*maker.getXs("yellow"))/10, 100)
    maker.execute(100)
    maker.release()
    # 2.
    maker.gotoGoal("hand", maker.getXs("blue"), 100)
    maker.execute(100)
    maker.grab("blue")
    # 3.
    maker.gotoGoal("hand", (2*maker.getXs("yellow") - maker.getXs("red")), 100)
    maker.execute(100)
    maker.release()
    # 4.    
    maker.gotoGoal("hand", [0, 0], 100)
    maker.execute(100)


if __name__ == "__main__":
    """
    maker = MakerMain.Maker()
    maker.debug_show()
    test1(maker)
    """
    for count in range(10):
        inits = {}
        inits["red"]    = [10000 * (random() - 0.5), 10000 * (random() - 0.5)]
        inits["blue"]   = [10000 * (random() - 0.5), 10000 * (random() - 0.5)]
        inits["yellow"] = [10000 * (random() - 0.5), 10000 * (random() - 0.5)]
        inits["green"]  = [10000 * (random() - 0.5), 10000 * (random() - 0.5)]
        for i in range(20):
            filename = "000"+"{0:03d}".format(count)+"{0:03d}".format(i)
            maker = MakerMain.Maker(filename)
            maker.debug_show()
            test2(maker, inits)
