#-*- coding: utf-8 -*-
from random import random
import glob

import HDP_HMM.MakerMotions as makerMotions
import HDP_HMM.MakerMain as makerMain

"""
print("---------- : Making datas")
inits = {}
inits["red"]    = [10000 * (random() - 0.5), 10000 * (random() - 0.5)]
inits["blue"]   = [10000 * (random() - 0.5), 10000 * (random() - 0.5)]
inits["yellow"] = [10000 * (random() - 0.5), 10000 * (random() - 0.5)]
inits["green"]  = [10000 * (random() - 0.5), 10000 * (random() - 0.5)]
for i in range(100):
    filename = "000000"+"{0:03d}".format(i)
    maker = makerMain.Maker(filename)
    maker.debug_show()
    makerMotions.test2(maker, inits)

import HDP_HMM.MakerPostProcess as post

print("++-------- : Post processing ")
filepaths = glob.glob("tmp/log_MakerMain/*")
for p in filepaths:
    print(p)
    if p[-4:] != ".csv":
        continue
    output = post.inputData(p)
    output = post.getHandData(output)
    output = post.getTMAList(output)
    output = post.getVelocityList(output)
    post.outputData(output, p)

"""
soinnN = 1250
soinnE = 1250

# SOINN のパラメータは 2500, 5000, 10000, 20000, 40000 で試す
for ne in range(5):
        soinnN *= 2
        soinnE *= 2
        step = 1
        # step は 3, 5, 7, 9, で試す
        for s in range(4):
                step += 2
                import HDP_HMM.EncodewithSOINN as soinn

                print("++++------ : Encoding with SOINN")
                soinn.execute(step = step, soinnN = soinnN, soinnE = soinnE)

                import HPYLM.tasks.ParsingfromSOINN_results as hpylm
                
                paramA = -1
                # paramA は 1, 3, 5, 7, 9 で試す
                for p in range(5):
                        paramA += 2
                        print("++++++---- : Parsing with HPYLM")
                        hpylm.execute(paramA = paramA)

                        import HPYLM.tasks.GettingIntermmediates as inter

                        print("++++++++-- : Getting intermmediates")
                        dirName = str(step) + "-"
                        dirName += str(soinnN) + "-"
                        dirName += str(soinnE) + "-"
                        dirName += str(paramA)
                        inter.execute(dirName)

                        print("++++++++++ : Finished")
