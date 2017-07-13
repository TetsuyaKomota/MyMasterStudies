#-*- coding: utf-8 -*-

"""
とりあえず設定だけ決めていこう
・空間には物体が4つとハンドの5つ
・2次元
・
"""

class Maker:
    def __init__(self):
        self.hand = [0,0]
        self.objects = {}
        self.colorList = []
        self.colorList.append("red")
        self.colorList.append("blue")
        self.colorList.append("green")
        self.colorList.append("yellow")
        for c in self.colorList:
            self.objects[c] = [0,0]

    # 色名から座標を取得
    def getXY(self, color):
        return self.objects[color]

    # 色名から座標指定
    def setXY(self, color, xy):
        self.objects[color] = xy
        return self

    # 色名から座標移動
    def addXY(self, color, xy):
        for d in range(len(xy)):
            self.objects[color][d] = self.objects[color][d] + xy[d]
        return self

    # デバッグ用．現在の座標状況を取得する
    def debug_show(self):
        print("==SHOW==")
        print("hand \t: " + str(self.hand))
        for i in range(len(self.colorList)):
            col = self.colorList[i]
            print(col + " \t: " + str(self.objects[col]))

if __name__ == "__main__":
    maker = Maker()
    # maker.debug_show()
    maker.setXY("red", [1, 2])
    maker.debug_show()
    maker.addXY("red", [1, 1])
    maker.debug_show()
