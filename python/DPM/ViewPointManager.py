#-*- coding: utf-8 -*-

import ViewPointEncoder as encoder
import glob
import dill

# Encoder 使って色々するやつ

# 指定したファイル群から，指定した観点で状態を取得する
def getStateswithViewPoint(filepathList, baseList, refList):
    output = []
    for fname in filepathList:
        with open(fname, "r", encoding="utf-8") as f:
            while True:
                line = f.readline()
                if line == "":
                    break
                bstate = encoder.encodeState(line)
                astate = encoder.translateforViewPoint(bstate,baseList,refList)
                data   = encoder.serialize(astate)
                output.append(data)
    return output

# 状態集合(エンコード，観点変換済み)の前後の組から，ガウス分布を学習する
def getDistribution(stateList):
    



if __name__ == "__main__":
    filepaths = glob.glob("tmp/log_MakerMain/GettingIntermediated/*")
    datas = getStateswithViewPoint(filepaths, ["hand"], [])
    print(datas)
    with open("tmp/log_MakerMain/dills/test_pov.dill", "wb") as f:
        dill.dump(datas, f)
