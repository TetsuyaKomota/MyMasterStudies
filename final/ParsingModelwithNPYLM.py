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
from models import RefactedRestaurant

D      = 1
A      = 5
Theta  = 1
PAD    = 3
LEN    = 2
MIN_W  = 2
n_iter = 200

def fit():
    with open("tmp/dills/encoded.dill", "rb") as f:
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
    with open("tmp/dills/npylm.dill", "wb") as f:
        dill.dump(rest, f)
    
    return rest

def parsing(dillname):
    if os.path.exists("tmp/dills/npylm.dill") == True:
        with open("tmp/dills/npylm.dill", "rb") as f:
            rest = dill.load(f)
    else:
        rest = fit()

    with open("tmp/dills/"+dillname, "rb") as f:
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

    # 分割をサンプリング
    result = rest.executeParsing(strDictZip, n_iter, fit=False)

    # 境界列に変換
    output = {}
    for i, d in enumerate(strDictZip.keys()):
        print(d)
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
        with open("tmp/dills/parsed_test.dill", "wb") as f:
            dill.dump(output, f)
    else:
        with open("tmp/dills/parsed.dill", "wb") as f:
            dill.dump(output, f)
    
    return output

if __name__ == "__main__":
    # train による学習
    # これ以降 train の推定結果は使用しないため，predict ではなく fit     
    fit()
    # test による推定
    parsing("encoded_test.dill")

