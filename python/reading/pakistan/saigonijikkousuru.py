# coding = utf-8

import warnings

from hmmlearn import hmm
import numpy as np
import random

STATE = 12
SIZE  = 55

bestState = 0
bestSize  = 0
bestOK    = 0

with warnings.catch_warnings():
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

    pre = []
    for _ in range(10):
        try:
            model.fit(datas)
            print("startprob_")
            print(model.startprob_)
            print("means_")
            print(model.means_)
            print("covars_")
            print(model.covars_)
            print("transmat_")
            print(model.transmat_)    

            pre = model.predict(datas)
            break
        except:
            print("Error...")

    # pre[-1] の次に最も遷移する確率の高い状態の，
    # 最も出力しやすい分布の平均値を推定結果とする
    laststate = pre[-1]
    nextstate = -1
    tempmax = 0
    for i, t in enumerate(model.transmat_[laststate]):
        if tempmax < t:
            nextstate = i
            tempmax = t
    nextmean = model.means_[nextstate]
    print(nextmean)
