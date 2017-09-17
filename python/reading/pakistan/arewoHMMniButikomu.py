# coding = utf-8

# 1. HMM で学習する
# 2. 最終状態に対して，次の遷移隔離が最も高い状態を取得する
# 3. 取得した状態からの出力確率分布から緯度経度を推定する

import warnings

from hmmlearn import hmm
import numpy as np
import random

STATE = 10
SIZE  = 20

bestState = 0
bestSize  = 0
bestOK    = 0

res = open("tmp/result.csv", "w", encoding="utf-8")

for st in range(10, 21):
    for si in range(1, 20):
        STATE = st
        SIZE  = 5*si
        print("step:(state, size)=("+str(STATE)+","+str(SIZE)+")")
        with warnings.catch_warnings():
        # for _ in range(1):
            warnings.simplefilter("ignore")

            model = hmm.GaussianHMM(STATE, covariance_type="full") 

            datas = []

            with open("tmp/are.csv", "r", encoding="utf-8") as f:
                while True:
                    line = f.readline()[:-1].split(",")
                    if len(line) < 2:
                        break
                    elif len(line) != 4:
                        print("おまわりさんこいつです!"+str(line))
                        continue
                    datas.append(np.array([float(line[2]), float(line[3])]))

            # print(datas)

            # size で分割
            size = SIZE
            splitdatas = []
            temp = [0]+datas[:size-1]
            for i in range(size, len(datas)):
                temp = temp[1:]
                temp.append(datas[i])
                splitdatas.append(temp)

            """
            for s in splitdatas:
                print(s)
            """
            random.shuffle(splitdatas)

            lengths = [size for _ in range(size)]

            pre = []
            for _ in range(10):
                try:
                    model.fit(np.concatenate(splitdatas), lengths)
                    """
                    print("startprob_")
                    print(model.startprob_)
                    print("means_")
                    print(model.means_)
                    print("covars_")
                    print(model.covars_)
                    print("transmat_")
                    print(model.transmat_)    

                    print("------------------")
                    for s in splitdatas:
                        print(np.exp(model.score(s)))
                    """
                    pre = model.predict(datas)
                    break
                except:
                    print("Error...")

            # print(pre)
             
            if pre == []:
                res.write(str(STATE)+","+str(SIZE)+","+str(0)+"\n")
                continue 
            ok = 0
            ng = 0 
            for i in range(len(pre)-1):
                # 遷移確率で推定
                t = model.transmat_[pre[i]]
                tempmax = 0
                for i, T in enumerate(t):
                    if tempmax < T:
                        q = i
                        tempmax = T

                if pre[i+1] == q:
                    ok += 1
                else:
                    ng += 1
            print("result:(ok,ng)=("+str(ok)+","+str(ng)+")")
            res.write(str(STATE)+","+str(SIZE)+","+str(ok)+"\n")
            if ok > bestOK:
                bestState = st
                bestSize = si
                bestOK = ok
        res.close()
        res = open("tmp/result.csv", "w", encoding="utf-8")
print("bestSTATE:" + str(bestState))
print("bestSIZE :" + str(bestSize))
print("bestOK   :" + str(bestOK))
res.close()
