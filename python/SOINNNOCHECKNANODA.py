#-*- coding: utf-8 -*-
from random import random
import glob
import dill

import HDP_HMM.MakerMotions as makerMotions
import HDP_HMM.MakerMain as makerMain
import HDP_HMM.EncodewithSOINN as soinn

# step, soinnN, soinnE, paramA のグリッドサーチ
# 結果は GettingIntermediated_20170901, SYUKEISURUNODA_20170901 参照
# step   : 3
# soinnN : 2500
# soinnE : 2500
# paramA : 9
# で最適だった．
# テストの範囲を修正し，paramTheta のループも加えて再度テストを行う

soinnN = 625
soinnE = 625

output = []

# SOINN のパラメータは 2500, 5000, 10000, 20000, 40000 で試す
for ne in range(6):
        step = 1
        # step は 1, 3, 5, 7, 9, で試す
        for s in range(4):
                print("++++------ : Encoding with SOINN")
                soinn.execute(step = step, soinnN = soinnN, soinnE = soinnE)
                num = 0
                with open("tmp/log_MakerMain/dills/SOINN_results.dill", "rb") as f:
                    data = dill.load(f)
                    temp = []
                    for d in data:
                        temp += data[d]
                    num = len(set(temp))
                output.append({"soinn":soinnN, "step":step, "numofClass":num})
                with open("tmp/SOINNNOCHECKNANODA.txt", "a", encoding="utf-8") as f:
                    f.write(str(soinnN)+","+str(step)+","+str(num)+"\n")
                print("appended:" + str(output[-1]))
                step += 2
        soinnN *= 2
        soinnE *= 2
for o in output:
    print(o)
