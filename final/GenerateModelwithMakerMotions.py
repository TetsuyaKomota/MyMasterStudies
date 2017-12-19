# coding = utf-8

# やること
# データ作る

# メソッド
# ・データ生成
#   tmp/log に，指定した動作を生成

import numpy as np
from numpy.random import choice
from random import random
import os

def generate():

    if os.path.exists("tmp/log") == False:
        os.mkdir("tmp/log")

    # ファイルを 5000 データ作成する
    for i in range(5000):
        filename = "tmp/log/"+"{0:05d}".format(i)+".csv"
        objList = ["red", "blue", "green", "yellow"]
        objNum  = len(objList)

        # ランダムに初期化
        rands = list((np.random.rand(objNum*2)-0.5) * 10000)
        inits = {"hand" : np.zeros(2)}
        for o in objList:
            inits[o] = np.array([rands.pop(), rands.pop()])

        # 動作をランダムに決定
        # いずれも「取りに行く→動かす→取りに行く→動かす→戻る」なので
        # 取りに行く物体，動かす先をランダムに決定する
        # choice の False は「重複不可」
        moves = []
        moves.append(choice(objList, 1, False))
        moves.append(choice(objList, max(1, choice(objNum+1)), False))
        moves.append(choice(objList, 1, False))
        moves.append(choice(objList, max(1, choice(objNum+1)), False))
        moves.append(choice(objList, 0, False))
 
        step = 0
        pick = "none"

        # 動作を行う 
        with open(filename, "w", encoding="utf-8") as f:
            for s in range(len(moves)):
                # hand の目的地(moves[s] の物体位置と 9:1 のところ)を求める
                subgoal = np.zeros(2)
                for o in moves[s]:
                    subgoal += inits[o]
                if len(moves[s]) > 0:
                    subgoal /= len(moves[s])
                subgoal -= inits["hand"]

                # 100 ステップで到達するための初速と加速度を求める
                v = subgoal/50
                a = subgoal/(-5000)

                # 100 ステップ実行する
                for _ in range(100):
                    # 出力
                    text  = str(step) + ","
                    text += str(inits["hand"][0])+","
                    text += str(inits["hand"][1])+","
                    text += str(v[0])+","
                    text += str(v[1])+","
                    for o in objList:
                        text += str(inits[o][0])+","+str(inits[o][1])+","
                    f.write(text+"\n") 

                    # ステップインクリメント
                    step += 1

                    # 移動
                    inits["hand"] += v
                    if pick != "none":
                        inits[pick] += v
                    v += a

                # step = 100, 300 なら掴み，200, 400 なら離す
                if step in [100, 300]:
                    pick = moves[s][0]
                else:
                    pick = "none"

if __name__ == "__main__":
    generate()
