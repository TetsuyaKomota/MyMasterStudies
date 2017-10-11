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

"""
2017/ 9/ 1
step, soinnN, soinnE, paramA のグリッドサーチ
結果は GettingIntermediated_20170901, SYUKEISURUNODA_20170901 参照
step   : 3
soinnN : 2500
soinnE : 2500
paramA : 9
で最適だった．
テストの範囲を修正し，paramTheta のループも加えて再度テストを行う

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
"""

"""
soinnN = 5000
soinnE = 5000
# 2017/ 9/11
# SOINN パラメータ，step, paramA の詳細値と，
# 新たに paramTheta を加えたグリッドサーチ
# 時間の関係上結局SOINN パラメータの詳細は取れてない
# SOINN のパラメータは 2500, 1250, 625 で試す
# 結果は GettingIntermediated_20170911, SYUKEISURUNODA_20170911 参照
for ne in range(3):
    soinnN /= 2
    soinnE /= 2
    step = 1
    # step は 2, 3, 4 で試す
    for s in range(3):
        step += 1
        import HDP_HMM.EncodewithSOINN as soinn

        print("++++------ : Encoding with SOINN")
        soinn.execute(step = step, soinnN = soinnN, soinnE = soinnE)

        import HPYLM.tasks.ParsingfromSOINN_results as hpylm
        
        paramA = 7
        # paramA は 9, 11, 13 で試す
        for p in range(5):
            paramA += 2
            # paramTheta は 1, 2, 3, 4, 5 で試す
            paramTheta = 0
            for pT in range(5):
                paramTheta += 1
                print("++++++---- : Parsing with HPYLM")
                hpylm.execute(paramA = paramA, paramTheta = paramTheta)

                import HPYLM.tasks.GettingIntermmediates as inter

                print("++++++++-- : Getting intermmediates")
                dirName = str(step) + "-"
                dirName += str(soinnN) + "-"
                dirName += str(soinnE) + "-"
                dirName += str(paramA) + "-"
                dirName += str(paramTheta)
                inter.execute(dirName)

                print("++++++++++ : Finished")
"""
"""
soinnN = 5000
soinnE = 5000
# SOINN のパラメータは 2500, 1250, 625 で試す
# 結果は GettingIntermediated_20170911, SYUKEISURUNODA_20170911 参照
for ne in range(3):
    soinnN /= 2
    soinnE /= 2
    step = 2
    # step は3 で試す
    for s in range(1):
        step += 1
        import HDP_HMM.EncodewithSOINN as soinn

        print("++++------ : Encoding with SOINN")
        soinn.execute(step = step, soinnN = soinnN, soinnE = soinnE)

        import HPYLM.tasks.ParsingfromSOINN_results as hpylm
        
        paramA = 9
        # paramA は11 で試す
        for p in range(1):
            paramA += 2
            # paramTheta は 1, 2, 3, 4, 5 で試す
            paramTheta = 0
            for pT in range(5):
                # Windows Update 死ね
                # もう終わってるところはスキップ
                paramTheta += 1
                if pT < 2:
                    continue
                # 繰り返しで結果が変わるかもなので，5回ずつ結果を出す
                for n_iter in range(5):
                    print("++++++---- : Parsing with HPYLM")
                    hpylm.execute(paramA = paramA, paramTheta = paramTheta)

                    import HPYLM.tasks.GettingIntermmediates as inter

                    print("++++++++-- : Getting intermmediates")
                    dirName = str(step) + "-"
                    dirName += str(int(soinnN)) + "-"
                    dirName += str(int(soinnE)) + "-"
                    dirName += str(paramA) + "-"
                    dirName += str(paramTheta) + "-"
                    dirName += str(n_iter)
                    inter.execute(dirName)

                    print("++++++++++ : Finished")
"""
# SOINN のパラメータは2000, 2500, 3000 で試す
soinnN = 1500
soinnE = 1500
for ne in range(3):
    soinnN += 500
    soinnE += 500
    step = 2
    # step は3 で試す
    for s in range(1):
        step += 1
        import HDP_HMM.EncodewithSOINN as soinn

        print("++++------ : Encoding with SOINN")
        soinn.execute(step = step, soinnN = soinnN, soinnE = soinnE)

        import HPYLM.tasks.ParsingfromSOINN_results as hpylm
        
        paramA = 9
        # paramA は11 で試す
        for p in range(1):
            paramA += 2
            # paramTheta は 2 で試す
            paramTheta = 1
            for pT in range(1):
                paramTheta += 1
                # paramNumS, T は 1, 3, 5, 7 で試す
                paramNum = -1
                for pN in range(4):
                    paramNum += 2
                    # 繰り返しで結果が変わるかもなので，5回ずつ結果を出す
                    for n_iter in range(5):
                        print("++++++---- : Parsing with HPYLM")
                        hpylm.execute(paramA = paramA, paramTheta = paramTheta, paramNum, paramNum)

                        import HPYLM.tasks.GettingIntermmediates as inter

                        print("++++++++-- : Getting intermmediates")
                        dirName = str(step) + "-"
                        dirName += str(int(soinnN)) + "-"
                        dirName += str(int(soinnE)) + "-"
                        dirName += str(paramA) + "-"
                        dirName += str(paramTheta) + "-"
                        dirName += str(n_iter)
                        inter.execute(dirName)

                        print("++++++++++ : Finished")
