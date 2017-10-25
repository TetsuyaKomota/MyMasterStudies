#-*- coding: utf-8 -*-
from random import random
import glob

import HDP_HMM.MakerMotions as makerMotions
import HDP_HMM.MakerMain as makerMain
import HDP_HMM.MakerPostProcess as post
import HDP_HMM.EncodewithSOINN as soinn
import HPYLM.tasks.ParsingfromSOINN_results as hpylm
import HPYLM.tasks.GettingIntermmediates as inter
import setting

NOPARAMS = "there is no paramater any more."
NAME     = 0
IDX      = 1

class ParamManager:
    def __init__(self):
        self.params  = setting.HONKORE_PARAMS
        self.counter = []

    def pick(self, paramList, key):
        # paramList のキーには自動割り振りの数字インデックスがついている
        # 利用時にそれがいくつかわからないため，キー名のみで指定できるように変更する
        for p in paramList.keys():
            if key in p:
                return paramList[p]
        return None

    def getParamNameList(self):
        return sorted(list(self.params.keys()))

    def firstParams(self):
        self.counter = [[p, 0] for p in self.params.keys()]
        output = {}
        for c in self.counter:
            output[c[NAME]] = self.params[c[NAME]][c[IDX]]
        return output

    def nextParams(self):
        return self.sub_nextParams(0)
 
    def sub_nextParams(self, i):
        # +1しても配列内に収まるなら
        if self.counter[i][IDX]+1<len(self.params[self.counter[i][NAME]]):
            self.counter[i][IDX] += 1
            output = {}
            for c in self.counter:
                output[c[NAME]] = self.params[c[NAME]][c[IDX]]
            return output
        # 収まらないなら
        else:
            if i >= len(self.counter)-1:
                return NOPARAMS
            self.counter[i][IDX] = 0
            return self.sub_nextParams(i+1)

    def printREADME(self):
        fpath = "tmp/log_MakerMain/GettingIntermediated/README.txt"
        with open(fpath, "w", encoding="utf-8") as f:
            f.write("ディレクトリのパラメータは以下の順に並んでいます\n")
            f.write(str(self.getParamNameList()))
            f.write("\n\n")
            f.write(setting.HONKORE_EXPLANATION)

def run():
    print("start HONKORE")
    pm = ParamManager()
    pm.printREADME()
    p  = pm.firstParams()
    count = 0
    while True:
        print("[HONKORE]iteration:" + str(count))
        count += 1
        if p == NOPARAMS:
            break
        print("---------- : Making datas")
        # makerMotions.execute(pm.pick(p, "testNumber"), pm.pick(p, "inits"), pm.pick(p, "numofData"))
        print("++-------- : Post processing ")
        # post.execute(False)
        print("++++------ : Encoding with SOINN")
        # soinn.execute(pm.pick(p, "step"), soinnN=pm.pick(p, "soinn"), soinnE=pm.pick(p, "soinn"))
        print("++++++---- : Parsing with HPYLM")
        hpylm.execute(D=pm.pick(p, "D"), A=pm.pick(p, "A"), Theta=pm.pick(p, "Theta"), \
                        PAD=pm.pick(p, "PAD"), hpylm_iter=pm.pick(p, "hpylm_iter"), reverse=pm.pick(p, "reverse"))
        print("++++++++-- : Getting intermmediates")
        inter.execute([p[name] for name in pm.getParamNameList()])
        print("++++++++++ : Finished")
        p = pm.nextParams()

if __name__ == "__main__":
    run()
