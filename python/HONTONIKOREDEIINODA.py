#-*- coding: utf-8 -*-

import HDP_HMM.MakerMotions as makerMotions
import HDP_HMM.MakerMain as makerMain
import HDP_HMM.MakerPostProcess as post
import HDP_HMM.EncodewithSOINN as soinn
import HPYLM.tasks.ParsingfromSOINN_results as hpylm
import HPYLM.tasks.GettingIntermmediates as inter
import setting
from ParamManager import ParamManager 
from ParamManager import NOPARAMS 

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
        # print("---------- : Making datas")
        # makerMotions.execute(pm.pick(p, "testNumber"), pm.pick(p, "isShuffleInits"), pm.pick(p, "numofData"))
        print("++-------- : Post processing ")
        post.execute()
        print("++++------ : Encoding with SOINN")
        soinn.execute(pm.pick(p, "step"), soinnN=pm.pick(p, "soinn"), soinnE=pm.pick(p, "soinn"))
        print("++++++---- : Parsing with HPYLM")
        hpylm.execute(D=pm.pick(p, "D"), A=pm.pick(p, "A"), Theta=pm.pick(p, "Theta"), \
                        PAD=pm.pick(p, "PAD"), hpylm_iter=pm.pick(p, "hpylm_iter"), reverse=pm.pick(p, "reverse"))
        # print("++++++++-- : Getting intermmediates")
        # inter.execute([p[name] for name in pm.getParamNameList()])
        print("++++++++++ : Finished")
        p = pm.nextParams()

if __name__ == "__main__":
    run()
