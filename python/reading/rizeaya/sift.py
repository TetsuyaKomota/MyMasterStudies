# coding = utf-8

import cv2
import glob
import os
import sys
import numpy as np

# charaIdx = ["aya", "azusa", "kurumi", "rize"]
charaIdx = ["aya", "rize"]

def getDataSet():
    output = []
    fpaths = glob.glob("tmp/face/resized/*")
    for fpath in fpaths:
        fname = os.path.basename(fpath)
        if fname[-4:] not in [".jpg", ".png", ".gif"] or len([i for i in charaIdx if i in fname]) == 0:
            print("invalid path:" + fname)
            continue
        output.append([charaIdx.index([i for i in charaIdx if i in fname][0]), fpath])
    return output


def main():
    # 訓練データのパスを取得
    train_set = getDataSet()
    # 辞書サイズ
    dictionarySize = len(set([i[0] for i in train_set]))
    # Bag Of Visual Words分類器
    bowTrainer = cv2.BOWKMeansTrainer(dictionarySize)
    # 特徴量抽出器
    detector = cv2.xfeatures2d.SIFT_create()
    # 各画像を分析
    for i, (classId, data_path) in enumerate(train_set):
        # 進捗表示
        sys.stdout.write(".")
        # 画像読み込み
        img = cv2.imread(data_path)
        # 特徴点とその特徴を計算
        keypoints, descriptors= detector.detectAndCompute(img,None)
        # intからfloat32に変換
        descriptors = descriptors.astype(np.float32)
        # 特徴ベクトルをBag Of Visual Words分類器にセット
        bowTrainer.add(descriptors)

    # Bag Of Visual Words分類器で特徴ベクトルを分類
    codebook = bowTrainer.cluster()
    # 訓練完了
    print("train finish")

    """
    test
    """
    print("test start")
    # テストデータのパス取得
    test_set = getDataSet()

    # KNNを使って総当たりでマッチング
    matcher = cv2.BFMatcher()

    # Bag Of Visual Words抽出器
    bowExtractor = cv2.BOWImgDescriptorExtractor(detector, matcher)
    # トレーニング結果をセット
    bowExtractor.setVocabulary(codebook)

    # 正しく学習できたか検証する
    c_all = 0
    c_suc = [0, 0, 0, 0]
    for i, (classId, data_path) in enumerate(test_set):
        # 読み込み
        img = cv2.imread(data_path)
        # 特徴点と特徴ベクトルを計算
        keypoints, descriptors= detector.detectAndCompute(img,None)
        # intからfloat32に変換
        descriptors = descriptors.astype(np.float32)
        # Bag Of Visual Wordsの計算
        bowDescriptors = bowExtractor.compute(img, keypoints)

        # 結果表示
        """
        className = {0: "aya",
                     1: "azusa",
                     2: "kurumi",
                     3: "rize"}
        """
        className = {}
        for i, c in enumerate(charaIdx):
            className[i] = c

        actual = "???"    
        maxIdx = [i for i, x in enumerate(bowDescriptors[0]) if x == max(bowDescriptors[0])]
        if len(maxIdx) == 1:
            actual = className[maxIdx[0]]

        result = ""
        c_all += 1
        if actual == "???":
            result = " => unknown."
        elif className[classId] == actual:
            result = " => success!!"
            c_suc[classId] += 1
        else:
            result = " => fail"

        print("expected: ", className[classId], ", actual: ", actual, result)
    print("result: " + str(sum(c_suc)) + "/" + str(c_all) + "--", end="")
    print(c_suc)

if __name__ == '__main__':
    main()
