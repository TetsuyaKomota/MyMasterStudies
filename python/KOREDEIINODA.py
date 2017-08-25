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
step = 5
soinnN = 5000
soinnE = 5000
paramA = 5

import HDP_HMM.EncodewithSOINN as soinn

print("++++------ : Encoding with SOINN")
soinn.execute(step = step, soinnN = soinnN, soinnE = soinnE)

import HPYLM.tasks.ParsingfromSOINN_results as hpylm

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
