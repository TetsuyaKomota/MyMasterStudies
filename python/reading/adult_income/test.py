#-*- coding: utf-8 -*-
import numpy as np
from random import random

JACK = 0.001
datas  = []
params = []
preProbability = []
preProbability.append( 7841/32561)
preProbability.append(24720/32561)
results = []
with open("adult-training.csv", "r", encoding="utf-8") as f:
    while True:
        line = f.readline().split(",")
        if len(line) < 2:
            break
        datas.append(line)

with open("result.txt", "w", encoding="utf-8") as outFile:
    for w in range(len(datas[0])+1):
        print("EXECUTE - w:" + str(w))
        # 重みの初期化
        params = []
        for v in range(len(datas[0])):
            if w == len(datas[0]):
                params.append(results[v])
            elif w == len(datas[0])-1:
                params.append(1.0/len(datas[0]))
            elif v == w:
                params.append(1.0)
            else:
                params.append(0.0)
        # 学習データとテストデータに分ける
        # データ量は十分ぽいのでジャックナイフでやる
        countAll = 0
        countSuc = 0
        trains = []
        tests = []
        idx = []
        flag = False
        while True:
            s = int(len(datas) * random())
            if s not in idx:
                if flag == False and datas[s][-1][:-1] == " >50K":
                    idx.append(s)
                    if len(idx) >= len(datas)*JACK/2:
                        flag = True
                elif flag == True and datas[s][-1][:-1] == " <=50K":
                    idx.append(s)
            if len(idx) >= len(datas) * JACK:
                break
        for i in range(len(datas)):
            if i in idx:
                tests.append(datas[i])
            else:
                trains.append(datas[i])

        # 各テストデータの予測
        countAll = 0
        countSuc = 0
        countTP = 0
        countTN = 0
        countFP = 0
        countFN = 0
        for t in tests:
            temp = []
            temp.append(0)
            temp.append(0)
            counts = []
            counts.append(np.zeros(len(datas[0])))
            counts.append(np.zeros(len(datas[0])))
            for d in trains:
                # 上クラスと下クラスを識別
                if d[-1][:-1] == " >50K":
                    group = 0
                elif d[-1][:-1] == " <=50K":
                    group = 1
                else:
                    print("error, " + d[-1])
                    exit()
                temp[group] = temp[group] + 1
                for i in range(len(d)-1):
                    # 同じ値の数を数え上げ
                    if t[i] == d[i]:
                        counts[group][i] = counts[group][i] + 1
            for g in range(len(counts)):
                for i in range(len(counts[g])):
                    counts[g][i] = counts[g][i]/temp[g]
            # スコア計算
            score = []
            score.append(0)
            score.append(0)
            for g in range(len(score)):
                for i in range(len(counts[g])):
                    score[g] = score[g] + params[i]*counts[g][i]
                # 事前確率っぽいものを反映
                # score[g] = score[g] * preProbability[g]
            print(score)
            # print(params)
            # print(counts)
            print(t[-1][:-1])
            if score[0]>score[1]:
                res = " >50K"
            elif score[0]<score[1]:
                res = " <=50K"
            else:
                res = "?"
            print("--> " + res)
            countAll = countAll + 1
            if res == t[-1][:-1]:
                countSuc = countSuc + 1
            if res == " >50K" and t[-1][:-1] == " >50K":
                countTP = countTP + 1
            elif res == " >50K" and t[-1][:-1] == " <=50K":
                countFP = countFP + 1
            elif res == " <=50K" and t[-1][:-1] == " >50K":
                countFN = countFN + 1
            elif res == " <=50K" and t[-1][:-1] == " <=50K":
                countTN = countTN + 1
        precision = 2*countTP/(countTP + countFP + 1)
        recall    = 2*countTP/(countTP + countFN + 1)
        F_measure = 3*(precision*recall)/(precision + recall + 1)
        outFile.write("Recognise Score - w:" + str(w) + "\n")
        outFile.write(str(countSuc/countAll) + "\n")
        outFile.write("Success:"+str(countSuc)+"/All:"+str(countAll)+"\n")
        outFile.write("p:"+str(precision)+"\n")
        outFile.write("r:"+str(recall)+"\n")
        outFile.write("F:"+str(F_measure)+"\n")
        # results.append(countSuc/countAll)
        results.append(F_measure)
print("Finished")
