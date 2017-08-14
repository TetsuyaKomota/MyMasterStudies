#-*- coding: utf-8 -*-
from random import random
import glob

import HDP_HMM.MakerMotions as makerMotions
import HDP_HMM.MakerMain as makerMain

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

import HDP_HMM.EncodewithSOINN as soinn

print("++++------ : Encoding with SOINN")
soinn.execute()

import HPYLM.tasks.ParsingfromSOINN_results as hpylm

print("++++++---- : Parsing with HPYLM")
hpylm.execute()

import HPYLM.tasks.GettingIntermmediates as inter

print("++++++++-- : Getting intermmediates")
inter.execute()

print("++++++++++ : Finished")
