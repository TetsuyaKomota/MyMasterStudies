# coding = utf-8
import cv2
import numpy as np
import os
import dill
import copy

"""
実行して
ESC : 終了
1   : 録画開始．新しい CSV ファイルが作られ，物体位置特定してステップログを保存
2   : 録画終了．CSV ファイルを閉じる．
3   : 動作再現開始．モデルをロードして最初の vp による目標を描画する
"""

DIR_PATH = "tmp/DEMO_result/"

# 指定の色の領域を取得
def find_rect_of_target_color(image, color):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV_FULL)
    h = hsv[:, :, 0]
    s = hsv[:, :, 1]
    mask = np.zeros(h.shape, dtype=np.uint8)
    if   color ==    "red":
        mask[((h <   5) | (h > 210)) & (s > 200)] = 255
    elif color ==   "blue":
        mask[((h > 150) & (h < 180)) & (s > 200)] = 255
    elif color ==  "green":
        mask[((h >  60) & (h < 130)) & (s > 128)] = 255
    elif color == "yellow":
        mask[((h >  30) & (h <  60)) & (s > 200)] = 255
    elif color ==   "hand":
        mask[(s < 0)] = 255
    _, contours, _ = cv2.findContours(mask, \
                        cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    rects = []
    for contour in contours:
        approx = cv2.convexHull(contour)
        rect = cv2.boundingRect(approx)
        rects.append(np.array(rect))
    return rects

# 動作再現のための位置補正
def rep(inputDict, model, step):
    state = model["viewpoint"][step]
    output = copy.deepcopy(inputDict)
    posDict = {}
    for p in inputDict.keys():
        posDict[p] = np.array(inputDict[p][:2])
 
    # base, ref の座標を取得
    base = np.zeros(2)
    ref  = np.zeros(2)
    for b in state["base"]:
        base += posDict[b]
    for r in state["ref"]:
        ref  += posDict[r]
    base /= len(state["base"])
    ref  /= len(state["ref"])
 
    # posDict に対して，base を引き，ref-base で回転
    ref = ref - base
    theta = np.arctan(ref[1]/ref[0])
    if ref[0] < 0:
        theta = theta + np.pi
    # 回転行列を作る
    if len(state["ref"]) == 0:
        rot = np.eye(2)
    else:
        rot = np.array([[np.cos(theta), np.sin(theta)], [-1*np.sin(theta), np.cos(theta)]])
    # 平行移動,回転させる
    for t in posDict.keys():
        posDict[t] = rot.dot(posDict[t] - base)
    # posDict に model["viewpoint"][step][~~] を加える
    for m in state["mean"]:
        posDict[m] += state["mean"][m]
    # posDict に対して，ref-base で逆回転，base を足す
    if len(state["ref"]) == 0:
        rot = np.eye(2)
    else:
        rot = np.array([[np.cos(theta), -1*np.sin(theta)], [np.sin(theta), np.cos(theta)]])
    for t in posDict.keys():
        posDict[t] = rot.dot(posDict[t]) + base

    print(posDict)
    for p in posDict.keys():
        output[p][0] = int(posDict[p][0])
        output[p][1] = int(posDict[p][1])
    return output

if __name__ == "__main__":
    colors = {}
    colors["red"   ] = (  0,   0, 255)
    colors["blue"  ] = (255,   0,   0)
    colors["green" ] = (  0, 255,   0)
    colors["yellow"] = (  0, 255, 255)
    colors["hand"  ] = (  0,   0,   0)

    capture = cv2.VideoCapture(0)

    if os.path.exists(DIR_PATH) == False:
        os.mkdir(DIR_PATH)

    step  = -1
    recFlag = False
    repFlag = False
    debug   = False

    # TODO この二つ要らない
    red    = [0, 0, 0, 0]
    yellow = [0, 0, 0, 0]

    while True:
        key = cv2.waitKey(30)
        if key == 27: # ESC
            break
        elif key == ord("1") and recFlag == False:
            recFlag = True
            step = -1
            count = 0
            while True:
                count += 1
                if os.path.exists(DIR_PATH+"{0:06d}".format(count) + ".csv") == False:
                    break
            f = open(DIR_PATH+"{0:06d}".format(count) + ".csv", "w", encoding="utf-8")
        elif key == ord("2") and recFlag == True:
            recFlag = False
            f.close()
        elif key == ord("3") and repFlag == False:
            # 動作再現を開始する
            # フラグを立てて matching モデルをロードする
            repFlag = True
            with open("tmp/dills/DEMO/model.dill", "rb") as f:
                model = dill.load(f)
        elif key == ord("4") and repFlag == True:
            repFlag = False
            model = None

        elif key == ord("9"):
            debug = not debug

        _, frame = capture.read()

        # recFlag または repFlag が立っている場合，物体位置をフレームで囲む
        if (recFlag or repFlag) == True:
            step += 1
            text = str(step) + ","
            # ログの順番を指定するために colors.keys() ではなくこの形
            rectDict = {}
            for c in ["hand", "red", "blue", "green", "yellow"]:
                rects = find_rect_of_target_color(frame, c)
                if len(rects) > 0:
                    rect = max(rects, key=(lambda x: x[2] * x[3]))
                else:
                    rect = np.array([0, 0, 0, 0])
                if rect[2] * rect[3] > 1000:
                    rect = rect
                else:
                    rect = np.array([0, 0, 0, 0])
                rectDict[c] = rect               
 
                text += (str(rect[0]+rect[2]/2)+",")
                text += (str(rect[1]+rect[3]/2)+",")
                text += "0,0,0,0,"
            # repDict == True なら 動作再現を行った目標位置に変換する
            if repFlag == True:
                rectDict = rep(rectDict, model, 1)
            for c in ["hand", "red", "blue", "green", "yellow"]:
                    rect = rectDict[c]
                    cv2.rectangle(frame, tuple(rect[0:2]), tuple(rect[0:2] + rect[2:4]), colors[c], thickness=2)

            # recFlag が立っている場合，ログ出力する
            if recFlag == True:
                f.write(text + "\n") 

        cv2.imshow('DEMO', frame)
    capture.release()
    f.close()
    cv2.destroyAllWindows()
