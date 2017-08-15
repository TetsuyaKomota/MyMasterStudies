#-*- coding: utf-8 -*-

import ViewPointEncoder as encoder
import glob

# Encoder 使って色々するやつ

# 指定したファイル群から，指定した観点で状態を取得する
def getStateswithViewPoint(filepathList, baseList, refList):
    output = []
    for fname in filepathList:
        with open(fname, "rb", encoding="utf-8") as f:
            while True:
                line = f.readline()
                if line == "":
                    break
                bstate = encoder.encodeState(line)
                astate = encoder.translateforViewPoint(bstate,baseList,refList)
                data   = encoder.serialize(astate)
                output.append(data)
    return output
if __name__ == "__main__":
    filepaths = glob.glob("tmp/log_MakerMain/GettingIntermediated/*")
    datas = getStateswithViewPoint(filepaths, ["hand"], [])
    print(datas)
