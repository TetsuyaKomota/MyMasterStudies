#-*- coding: utf-8 -*-

import MyHMM
import dill
import warnings
import re

# 状態数を変化させた際に符号化への影響を調べる

"""
model = MyHMM.MyHMM(30)
with open("../tmp/HMM_results.dill", "rb") as f:
    hmm_results = dill.load(f)
for m in range(1, len(hmm_results)+1):
    for d in hmm_results["make"+str(m)]:
        print(d)

exit()
"""
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    results = {}
    for n in range(1,11):
        num = n*5
        model = MyHMM.MyHMM(num)
        model.experiment_0(False)
        with open("tmp/HMM_results.dill", "rb") as f:
            hmm_results = dill.load(f)
        # 状態数をキーに設定
        results[num] = {}
        results[num]["examples"] = []
        # 符号長を取得
        results[num]["lengths"] = []
        for m in range(1, len(hmm_results)+1):
            # 取り合えずの符号列の例を一つずつ取得
            results[num]["examples"].append(hmm_results["make"+str(m)][0])
            length = 0
            count = 0
            for d in hmm_results["make"+str(m)]:
                length = length + len(d)
                count = count + 1
            results[num]["lengths"].append(length/count)
        # 一度しか登場しない文字の比率と
        # 一度も登場しない文字の比率を調べる
        # results[num]["rate_0"] = []
        # results[num]["rate_1"] = []
        hist = {}
        for m in range(1, len(hmm_results)+1):
            for d in hmm_results["make"+str(m)]:
                """
                import copy
                mrd = copy.deepcopy(d)
                mrd.sort()
                print(mrd)
                """
                for c in d:
                    if c not in hist.keys():
                        hist[c] = len([x for x in d if x == c])
                    else:
                        hist[c] = max(hist[c], len([x for x in d if x == c]))
        results[num]["rate_0"] = (num - len(hist))/num
        results[num]["rate_1"] = len([x for x in hist if hist[x] == 1])/num


    print("====lengths====")
    for n in range(1, 11):
        N = n*5
        print(str(N) + ":" + str(results[N]["lengths"]))
    print("====rate_0====")
    for n in range(1, 11):
        N = n*5
        print(str(N) + ":" + str(results[N]["rate_0"]))
    print("====rate_1====")
    for n in range(1, 11):
        N = n*5
        print(str(N) + ":" + str(results[N]["rate_1"]))
    # 結果を csv 出力
    with open("tmp/results.csv", "w") as f:
        for n in range(1, 11):
            N = n*5
            f.write(str(N) + ",")
            for l in results[N]["lengths"]:
                f.write(str(l) + ",")
            f.write(str(results[N]["rate_1"]) + ",")
            for e in results[N]["examples"]:
                f.write(re.sub(",", ".", str(e)) + ",")
            f.write("\n")
