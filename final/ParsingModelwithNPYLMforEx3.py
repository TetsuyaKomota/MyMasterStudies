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

# 符号列に初期状態として一定の割合で境界をつけておく

import dill
import os
import glob
import shutil
from models import RefactedRestaurant
import numpy as np

D      =  1
Theta  = 20
PAD    =  3
MIN_W  =  2


def fit(dillpath, LEN, n_iter, tRate):
    with open("tmp/dills/"+dillpath+"encoded.dill", "rb") as f:
        encoded = dill.load(f)

    rest =RefactedRestaurant.Franchise(D, Theta, PAD, LEN, MIN_W)
 
    # 文字列化
    strDict = {}
    for filename in encoded.keys():
        line = ""
        for s in encoded[filename]:
            line += rest.translate(s)
        strDict[filename] = [line]

    # 冗長性の削除の前に，教師データとして境界を入れる
    # 教師データは 教師データ率 * ログ数 * int(ログ長さ/200)
    step = len(list(encoded.values())[0])
    tNum = tRate * len(encoded.keys()) * int(step/200)

    # tNum 個分の境界を選択
    tDict  = {}
    tCount = 0
    while tCount < tNum:
        k = np.random.choice(list(strDict.keys()), 1)[0]
        if k not in tDict.keys():
            tDict[k]  = 1
            tCount += 1
        elif tDict[k] < int(step/200):
            tDict[k] += 1
            tCount += 1

    # 境界を分割
    for k in tDict.keys():
        idxList = list(range(int(step/200)))
        np.random.shuffle(idxList)
        idxList = sorted(idxList[:tDict[k]])
        temp = []
        bIdx = 0
        aIdx = 0
        while len(idxList) > 0:
            bIdx = aIdx
            aIdx = (idxList.pop(0)+1)*200
            temp.append(strDict[k][0][bIdx:aIdx])
        temp.append(strDict[k][0][aIdx:])
        strDict[k] = temp

    # 冗長性を削除
    strDictZip = {}
    for filename in strDict.keys():
        strList = strDict[filename]
        strDictZip[filename] = []
        for t in strList:
            cList=[t[i] for i in range(len(t)) if i==0 or t[i] != t[i-1]]
            # [char] -> str -> [str]
            strDictZip[filename].append("".join(cList))

    # 調整
    # すべて，同じ文字の羅列の途中で切れているので，
    # 片方に寄せる．基本的には手前に寄せて，
    # 空文字になってしまう場合だけ後ろに寄せる
    for filename in strDictZip.keys():
        temp = []
        for i in range(len(strDictZip[filename])):
            if i == 0 or len(strDictZip[filename][i]) <= 1:
                if len(temp) > 0:
                    temp[-1] = temp[-1][:-1]
                temp.append(strDictZip[filename][i])
            else:
                temp.append(strDictZip[filename][i][1:])
        strDictZip[filename] = temp

    # 一旦表示
    for k in strDictZip.keys():
        print(k)
        if k in tDict.keys():
            print(tDict[k])
        else:
            print(0)
        print(strDict[k])
        print(strDictZip[k])

    # 調整
    # 短すぎる文があるとまずいっぽい
    rm = []
    for s in strDictZip.keys():
        temp = "".join(strDictZip[s])
        if len(temp) < 3:
            rm.append(s)
    for s in rm:
        del strDictZip[s]

    # 学習
    result = rest.executeParsing(strDictZip, n_iter)
    
    # return
    with open("tmp/dills/"+dillpath+"npylm.dill", "wb") as f:
        dill.dump(rest, f)
    
    return rest

def parsing(dillpath, dillname, LEN, n_iter, tRate):
    if os.path.exists("tmp/dills/"+dillpath+"npylm.dill") == True:
        with open("tmp/dills/"+dillpath+"npylm.dill", "rb") as f:
            rest = dill.load(f)
    else:
        rest = fit(dillpath, LEN, n_iter, tRate)

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

        # 最後の境界が 200n+100 になるっぽいので
        # 200n+99 に調整
        m[-1] -= 1
        # なんか調整
        if m[-1] != 699:
            m.append(699)
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
    filepaths = [p for p in filepaths if "Kmeans_" in p]
    for p in [filepaths[0]]:
        if p[-1] == "/":
            kmeanspath = p
        else:
            kmeanspath = p + "/"
        # 力わざでディレクトリ名からKmeansのパラメータを取得する
        k = kmeanspath[:-1].split("_")[1].split("=")[1]
        for tRate in [0.1*r for r in range(11)]:
            dirpath  = "NPYLM_k="+str(k)+",LEN_2=,ITER=200,tRate="+str(tRate)
            dirpath += "/"
            if os.path.exists("tmp/dills/"+dirpath) == False:
                os.mkdir("tmp/dills/"+dirpath)
                shutil.copyfile(kmeanspath+"encoded.dill",      "tmp/dills/"+dirpath+"encoded.dill")
                shutil.copyfile(kmeanspath+"encoded_test.dill", "tmp/dills/"+dirpath+"encoded_test.dill")
            # train による学習
            parsing(dirpath, "encoded.dill", 2, 200, tRate)
            # test による推定
            parsing(dirpath, "encoded_test.dill", 2, 200, tRate)


