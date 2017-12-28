# coding = utf-8

# やること
# 符号列 → 単語列

# メソッド
# ・学習
#   tmp/dills/encoded.dill で log の全部の符号列をロード
#   全部 NPYLM に代入
#   できた NPYLM を dill.dump
#
# ・解析
#   tmp/dills/npylm.dill をロード
#   tmp/dills/encoded.dill で log の全部の符号列をロード
#   全部を分かち書き
#   それを dill.dump

import dill
import os
import glob
import shutil
from models import RefactedRestaurant

D      = 1
A      = 5
Theta  = 1
PAD    = 3
MIN_W  = 2


def fit(dillpath, LEN, n_iter):
    with open("tmp/dills/"+dillpath+"encoded.dill", "rb") as f:
        encoded = dill.load(f)

    rest =RefactedRestaurant.Franchise(D, A, Theta, PAD, LEN, MIN_W)
    
    # 文字列化
    strDict = {}
    for filename in encoded.keys():
        line = ""
        for s in encoded[filename]:
            line += rest.translate(s)
        strDict[filename] = line

    # 冗長性を削除
    strDictZip = {}
    for filename in strDict.keys():
        t = strDict[filename]
        strDictZip[filename] = \
            [t[i] for i in range(len(t)) if i == 0 or t[i] != t[i-1]]
        
        # [char] -> str -> [str]
        strDictZip[filename] = \
            ["".join(strDictZip[filename])]

    # 調整
    # 短すぎる文があるとまずいっぽい
    rm = []
    for s in strDictZip.keys():
        if len(strDictZip[s][0]) < 3:
            rm.append(s)
    for s in rm:
        del strDictZip[s]

    # 学習
    result = rest.executeParsing(strDictZip, n_iter)
    
    # return
    with open("tmp/dills/"+dillpath+"npylm.dill", "wb") as f:
        dill.dump(rest, f)
    
    return rest

def parsing(dillpath, dillname, LEN, n_iter):
    if os.path.exists("tmp/dills/"+dillpath+"npylm.dill") == True:
        with open("tmp/dills/"+dillpath+"npylm.dill", "rb") as f:
            rest = dill.load(f)
    else:
        rest = fit(dillpath, LEN, n_iter)

    with open("tmp/dills/"+dillpath+dillname, "rb") as f:
        encoded = dill.load(f)

    # 文字列化
    strDict = {}
    for filename in encoded.keys():
        line = ""
        for s in encoded[filename]:
            line += rest.translate(s)
        strDict[filename] = line

    # 冗長性を削除
    strDictZip = {}
    for filename in strDict.keys():
        t = strDict[filename]
        strDictZip[filename] = \
            [t[i] for i in range(len(t)) if i == 0 or t[i] != t[i-1]]
        
        # [char] -> str -> [str]
        strDictZip[filename] = \
            ["".join(strDictZip[filename])]

    # 調整
    # 短すぎる文があるとまずいっぽい
    rm = []
    for s in strDictZip.keys():
        if len(strDictZip[s][0]) < 3:
            rm.append(s)
    for s in rm:
        del strDictZip[s]

    # 分割を推定
    result = rest.predict(strDictZip)

    # 境界列に変換
    output = {}
    for i, d in enumerate(strDictZip.keys()):
        m = [0]
        naive = strDict[d]
        sentence = result[d]
        step = 0
        for word in sentence:
            for c in word:
                while True:
                    if step < len(naive) and naive[step] == c:
                        step += 1
                    else:
                        break
            m.append(step)
        # 最後の境界が 500 になるっぽいので，
        # 499 に変更
        m[-1] -= 1
        output[d] = m
    
    # return 
    if "test" in dillname:
        with open("tmp/dills/"+dillpath+"parsed_test.dill", "wb") as f:
            dill.dump(output, f)
    else:
        with open("tmp/dills/"+dillpath+"parsed.dill", "wb") as f:
            dill.dump(output, f)
    
    return output

if __name__ == "__main__":
    filepaths = glob.glob("tmp/dills/*")
    filepaths = [p for p in filepaths if "SOINN_" in p]
    for p in filepaths:
        if p[-1] == "/":
            soinnpath = p
        else:
            soinnpath = p + "/"
        # 力わざでディレクトリ名からSOINNのパラメータを取得する
        soinnN = soinnpath[:-1].split("_")[1].split(",")[0].split("=")[1]
        soinnE = soinnpath[:-1].split("_")[1].split(",")[1].split("=")[1]
        for LEN in [2, 5, 100]:
            for ITER in [20, 200, 2000]:
                dirpath  = "NPYLM_LEN="+str(LEN)+",ITER="+str(ITER)
                dirpath += ", soinnN="+str(soinnN)
                dirpath += ", soinnE="+str(soinnE)
                dirpath += "/"
                os.mkdir("tmp/dills/"+dirpath)
                shutil.copyfile(soinnpath+"encoded.dill",      "tmp/dills/"+dirpath+"encoded.dill")
                shutil.copyfile(soinnpath+"encoded_test.dill", "tmp/dills/"+dirpath+"encoded_test.dill")
                # train による学習
                parsing(dirpath, "encoded.dill", LEN, ITER)
                # test による推定
                parsing(dirpath, "encoded_test.dill", LEN, ITER)

