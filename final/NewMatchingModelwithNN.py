# coding = utf-8

# やること
# 境界列(剪定済み) → 境界列(マッチング済み)

# 手順
# 0. 初期状態を before に入れる
# 1. before から十分離れた次の状態を after に入れる
# 2. 以下を複数回繰り返し，学習モデルを複数得る
#   2-1. before から重複サンプリング
#   2-2. サンプリング結果に対応した after を取得
#   2-3. 取得したデータセットでモデルを学習
#   2-4. 再代入で評価して評価値を得ておく
# 3. before それぞれに以下を行い，predict を取得
#   3-1. モデルで推定し，評価値で重みづけ
#   3-2. 和を predict に挿入
# 4. before を output に追加
# 5. before <- predict
# 6.1. に戻る

import os
import dill
import glob
import numpy as np
from functools import reduce
from time import sleep

e          = 30  # 許容誤差

def isDefferent(b, a):
    d = max([(b[i]-a[i])**2 for i in range(len(b))])
    return d>10

def matching(dillpath, n_iter):
    # データのロード
    with open("tmp/dills/"+dillpath+"parsed_test.dill", "rb") as f:
        prunned = dill.load(f)
    keys = prunned.keys()
    size      = 0   # データの次元． 2*オブジェクト数
    goal      = 0   # 終了状態のステップ数
    datas = {}
    for filename in keys:
        datas[filename] = []
        goal = prunned[filename][-1]
        filepath = "tmp/log_test/" + filename + ".csv"
        with open(filepath, "r", encoding="utf-8") as f:
            while True:
                line = f.readline().split(",")
                if len(line) < 2:
                    break
                if size == 0:
                    size = len(line[5:-1])
                datas[filename].append([float(l) for l in line[5:-1]])

    # 共通境界推定
    output = {}
    before = {}
    for filename in keys:
        output[filename] = []
        before[filename] = prunned[filename][0]
    while True:
        # 現段階の before を保存
        for filename in keys:
            output[filename].append(before[filename])
        after = {}
        for fn in keys:
            # before+e より大きい最小の step 
            # before+e 以降に境界がないなら終了状態にする
            later = [s for s in prunned[fn] if s > before[fn]+e \
                and isDefferent(datas[fn][before[fn]], datas[fn][s])]
            if len(later) > 0:
                after[fn] = later[0]
            else:
                after[fn] = prunned[fn][-1]

        for filename in before.keys():
            print(str(before[filename])+"\t--> "+str(after[filename]))
        # sleep(10)
 
        # 終了条件
        flagList = [goal-a < 50 for a in after.values()]
        flag = reduce(lambda x, y : x and y, flagList)
        if flag == True:
            # 最終結果を出力する
            for filename in keys:
                output[filename].append(after[filename])
            break

        # ---------------------------------------------------
        # 要するに，この部分を一回しかやらないのが間違ってる
        # ・サンプリングにより predict を取得
        # ・predict を after にしてもう一度サンプリング
        # ・predict = after になるまで繰り返す
        # ・predict を output に追加
        # ・before <- predict

        model = np.eye(size)
        # 学習率
        alpha = 1
        while True:
            # サンプリング学習を n_iter 回行う
            modelList = []
            for _ in range(n_iter):

                # size 個サンプリングして連立方程式を解く
                keyList = list(keys)
                np.random.shuffle(keyList)
                X = []
                y = []
                for k in keyList[:size]:
                    X.append(datas[k][before[k]]) 
                    y.append(datas[k][after[k]]) 

                # ここの転置忘れてた
        
                X    = np.array(X).T 
                y    = np.array(y).T

                Xinv = np.linalg.inv(X)
                A    = y.dot(Xinv)
     
                # 解いた結果の A で全データに対して再現精度を求める
                res = 0
                for k in keys:
                    b = np.array(datas[k][before[k]])
                    a = np.array(datas[k][after[k]])
                    r = A.dot(b)
                    res += np.linalg.norm(r-a)
                modelList.append((A, 1.0/res))

            sumexp = sum([m[1] for m in modelList])
            model *= 1-alpha
            for m in modelList:
                model += alpha * (m[1]/sumexp) * m[0]
            alpha *= 0.9

            # 次を推定する
            predict = {}
            for filename in keys:
                predict[filename] = []

                beforeData = datas[filename][before[filename]]
                """
                for m in modelList:
                    beforeData = datas[filename][before[filename]]
                    beforeData = np.array(beforeData)
                    predict[filename].append(m[0].dot(beforeData))
                    predict[filename][-1] *= m[1]/sumexp
                predict[filename] = sum(predict[filename])
                """
                predict[filename] = model.dot(beforeData)
        
            # 推定結果に最も近い状態を datas から取得
            selected = {}
            for filename in keys:
                # 各ステップの状態との距離を計算する
                p = np.array(predict[filename])
                d = datas[filename]
                distList = [np.linalg.norm(np.array(l)-p) for l in d]
                # before ステップ以降のみを対象にする
                distList = distList[before[filename]+e:]
                # after を選ぶ段階で else によって 499 になっている場合
                # [before+e:] に要素が存在しない．その時は
                # そのまま before を返す 
                if len(distList) == 0:
                    selected[filename] = before[filename]
                    continue
                selected[filename]  = distList.index(min(distList))
                # before+e ステップ分抜かしているので足しておく
                selected[filename] += before[filename]+e
 
            # after == selected なら break
            if after == selected:
                break
            # after = predict にして元に戻す
            after = selected

        # ---------------------------------------------------

        # before <- selected
        before = selected

  
    with open("tmp/dills/"+dillpath+"matching.dill", "wb")  as f:
        dill.dump(output, f)

    return output

if __name__ ==  "__main__":
    # matching("CHEAT/", 10) 
    # exit()
    filepaths = glob.glob("tmp/dills/*")
    for filepath in filepaths:
        if os.path.isdir(filepath) == False:
            continue
        if os.path.exists(filepath + "/parsed_test.dill") == True:
            dirname = os.path.basename(filepath)
            matching(dirname+"/", 1000)
