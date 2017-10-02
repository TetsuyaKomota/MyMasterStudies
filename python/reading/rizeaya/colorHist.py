# coding = utf-8

import cv2
import matplotlib.pyplot as plt
import glob
import os
import copy
import numpy as np
import random

def show_histogram(path):
    im = cv2.imread(path)
    if im.ndim == 2:
        # グレースケール
        plt.hist(im.lavel(), 256, range=(0, 255), fc='k')
        plt.show()
    elif im.ndim == 3:
        # カラー
        fig = plt.figure()
        fig.add_subplot(311)
        plt.hist(im[:,:,0].ravel(), 256, range=(0, 255), fc='b')
        plt.xlim(0,255)
        fig.add_subplot(312)
        plt.hist(im[:,:,1].ravel(), 256, range=(0, 255), fc='g')
        plt.xlim(0,255)
        fig.add_subplot(313)
        plt.hist(im[:,:,2].ravel(), 256, range=(0, 255), fc='r')
        plt.xlim(0,255)
        plt.show()

def getHistogram(path):
    im = cv2.imread(path)
    output = {}
    output["R"] = [i[0] for i in cv2.calcHist([im], [2], None, [256], [0, 256])]
    output["G"] = [i[0] for i in cv2.calcHist([im], [1], None, [256], [0, 256])]
    output["B"] = [i[0] for i in cv2.calcHist([im], [0], None, [256], [0, 256])]
    return output

def distance(hist1, hist2):
    output = {"R":0, "G":0, "B":0}
    for i in ["R", "G", "B"]:
        for j in range(256):
            output[i] += min(hist1[1][i][j], hist2[1][i][j])
        output[i] /= sum(hist1[1][i])
    return 1/(sum(output.values())/3)

# 生成したヒストグラムリストから kNN を計算する
def calc_kNN(histList, hist, k=10):
    temp = {}
    for h in histList:
        d = distance(hist, h)
        if len(temp) < k or d < max(temp.keys()):
            if len(temp) == k:
                del temp[max(temp.keys())]
            temp[d] = h
    # 近傍に最も多くあらわれたキャラも取得しておく
    count = {}
    for t in temp:
        if temp[t][0] not in count.keys():
            count[temp[t][0]] = 1
        else:
            count[temp[t][0]] += 1
    
    return [max(count.items(), key=lambda x:x[1])[0], min(temp.keys()), list(temp.values())]

if __name__ == "__main__":
    charaIdx = ["aya", "azusa", "kurumi", "rize"]
    # データを取得する
    fpaths = glob.glob("tmp/face/resized/*")
    # ヒストグラムに変換する
    hists = []
    for fpath in fpaths:
        chara = [i for i in charaIdx if i in fpath]
        if len(chara) == 0:
            print("invalid path:" + fpath)
        hists.append([charaIdx.index(chara[0]), getHistogram(fpath)])

    f = open("tmp/result.csv", "w", encoding="utf-8")
    f.write("all,")
    for c in charaIdx:
        f.write(c+",")
    f.write("\n")
    for _ in range(50):
        # ヒストグラムをシャッフルする
        random.shuffle(hists)
        # クロスバリデーション
        # データを適当なサイズに分ける
        hists_split = []
        part = 5
        size = int(len(hists)/part)
        for i in range(part):
            if i == part-1:
                hists_split.append(hists[i*size:])
            else:
                hists_split.append(hists[i*size:(i+1)*size])
       
        cross_res = {"all":0}
        for c in charaIdx:
            cross_res[c] = 0 
        for sp in range(part):
            # テストデータを分ける
            """
            test_rate = 0.2
            hists_train = copy.deepcopy(hists)
            hists_test  = []
            while True:
                if len(hists_test)/(len(hists_train)+len(hists_test)) >= test_rate:
                    break
                hists_test.append(hists_train.pop(np.random.choice(range(len(hists_train)))))
            """
            hists_test  = hists_split[sp]
            # hists_train = [h for h in hisp for hisp in (hists_split[:sp]+hists_split[sp+1:])]
            hists_train = sum(hists_split[:sp]+hists_split[sp+1:], [])

            # テスト誤差を検証してみる
            c_all = {}
            c_suc = {}
            for c in charaIdx:
                c_all[c] = 0
                c_suc[c] = 0
            for h in hists_test:
                # 最近傍 k データ取得
                nns = calc_kNN(hists_train, h)
                # 最近傍に頻出のキャラと推定
                predict = charaIdx[nns[0]]
                truth   = charaIdx[h[0]]
                print("truth:  "+truth+"  -->predict:  "+predict, end="")
                c_all[truth] += 1
                if predict == truth:
                    c_suc[truth] += 1
                    print("   Success!")
                else:
                    print("   Failed...")
            print("result:"+str(sum(c_suc.values()))+"/"+str(sum(c_all.values()))+"--", end="")
            # f.write(str(sum(c_suc.values())/sum(c_all.values()))+",")
            cross_res["all"] += sum(c_suc.values())/sum(c_all.values())
            for c in charaIdx:
                print("  " + c + ":" + str(c_suc[c]/c_all[c]), end="")
                # f.write(str(c_suc[c]/c_all[c])+",")
                cross_res[c] += (c_suc[c]/c_all[c])
            print("")
        f.write("all,"+str(cross_res["all"]/part)+",")
        for c in charaIdx:
            f.write(c+","+str(cross_res[c]/part)+",")
        f.write("\n")
    f.close()
