# -*- coding:utf-8 -*-
import cv2
import sys
import os
import shutil
import glob

imgPaths = glob.glob("tmp/*")
# cascade_path = "/usr/local/opt/opencv/share/OpenCV/haarcascades/haarcascade_frontalface_alt.xml"
# cascade_path = "tmp/cascades/haarcascade_frontalface_alt.xml"
cascade_path = "tmp/cascades/lbpcascade_animeface.xml"

for ipath in imgPaths:
    if ipath[-4:] not in [".jpg", ".png", ".gif"]:
        print("Not image:" + ipath)
        continue
    imgName = os.path.basename(ipath)
    #ファイル読み込み
    image = cv2.imread(ipath)
    if(image is None):
        print("cannot open:" + ipath)
        continue

    #グレースケール変換
    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    #カスケード分類器の特徴量を取得する
    cascade = cv2.CascadeClassifier(cascade_path)
    
    #物体認識（顔認識）の実行
    facerect = cascade.detectMultiScale(image_gray, scaleFactor=1.2, minNeighbors=2, minSize=(10, 10))
    # facerect = cascade.detectMultiScale(image_gray, scaleFactor=1.2)
    
    print("face rectangle")
    print(facerect)

    #ディレクトリの作成
    """
    if len(facerect) > 0:
        path = os.path.splitext(image_path)
        dir_path = path[0] + '_face'
        if os.path.isdir(dir_path):
            shutil.rmtree(dir_path)
        os.mkdir(dir_path)
    """

    i = 0;
    for rect in facerect:
        #顔だけ切り出して保存
        x = rect[0]
        y = rect[1]
        pad = 0.1
        width = rect[2]
        height = rect[3]
        dst = image[y:y+height, x:x+width]
        new_image_path = 'tmp/face/' + imgName[:-4] + "_" + str(i) + imgName[-4:]
        cv2.imwrite(new_image_path, dst)
        i += 1
