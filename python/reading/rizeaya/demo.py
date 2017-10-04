# coding = utf-8

import cv2
import matplotlib.pyplot as plt
import glob
import os
import copy
import numpy as np
import random

def show_histogram(im):
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

def getHistogram(im):
    if isinstance(im, str):
        im = cv2.imread(im)
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
    
    return [max(count.items(), key=lambda x:x[1])[0], min(temp.keys()), list(temp.values()), sum(temp.keys())/len(temp)]

def pick_face_resize(path):
    im = cv2.imread(path)
 
    cascade_path = "tmp/cascades/lbpcascade_animeface.xml"
   
    #グレースケール変換
    image_gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

    #カスケード分類器の特徴量を取得する
    cascade = cv2.CascadeClassifier(cascade_path)
    
    #物体認識（顔認識）の実行
    facerect = cascade.detectMultiScale(image_gray, scaleFactor=1.2, minNeighbors=2, minSize=(10, 10))
 
    # 取得するのは最初の顔(多分一番左上の顔)
    if len(facerect) < 1:
        return None
    rect = facerect[0]

    #顔だけ切り出して保存
    x = rect[0]
    y = rect[1]
    width = rect[2]
    height = rect[3]
    dst = im[y:y+height, x:x+width]
    size = (800, 800)
    inter = cv2.INTER_LINEAR
    resized = cv2.resize(dst, size, interpolation = inter)
    return resized

if __name__ == "__main__":
    charaIdx = ["arai", "kaban", "serval", "zerda"]
    # データを取得する
    fpaths = glob.glob("tmp/face/resized/*")
    # ヒストグラムに変換する
    hists = []
    for fpath in fpaths:
        chara = [i for i in charaIdx if i in fpath]
        if len(chara) == 0:
            print("invalid path:" + fpath)
        hists.append([charaIdx.index(chara[0]), getHistogram(fpath)])

    while True:
        print("どの画像を試す？")
        print("> ", end="")
        fname = input()
        if fname == "bye":
            print("じゃーね！")
            break
        elif fname == "":
            print("")
            continue
        elif os.path.exists("tmp/demo/"+fname) == False:
            print("そんなファイルないよ？")
            print("")
            continue
        im   = pick_face_resize("tmp/demo/"+fname)
        if im is None:
            print("ごめん，顔が見つからなかったよ")
            print("")
            continue
        cv2.imshow("face", im)
        hist = [-1, getHistogram(im)]
        nns  = calc_kNN(hists, hist)
        charaName = ["アライさん", "かばんちゃん", "サーバルちゃん", "フェネック"]
        if nns[3] <= 1.65:
            name = charaName[nns[0]]
            print("これは，" + name + "！！")
        else:
            print("これは，まだ知らない人！！")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        # print(nns[1])
        # print(nns[3])
        print("")
