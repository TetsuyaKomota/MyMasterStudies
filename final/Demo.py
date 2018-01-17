# coding = utf-8
import cv2
import numpy as np
import os
import dill
import copy
import glob
from functools import reduce


"""
デモのながれ
1. 画面表示される
2. 「1」押すと物体認識開始
3. 「2」押すと物体認識終了して記録, 調整(499 ステップに変更)
4. 「1」と「2」を繰り返してデータためる
5. 「3」でモデル作成
6. 「4」でモデルを用いた再現を開始

モデル作成について
超力づくでいいので実装しよう
1. 各ログファイルから．状態の静止していた区間の最初の状態を取得してくる
2. EM する <- 移動物体で識別するだけで OK
3. 移動物体と関数(テンソル)の対を各境界間で作成
4. そのリストを model として出力

再現について
model は各ステップにおいて移動物体が明示されている
1. 移動物体の色の枠で表した目標位置を描画（円形とかで）
2. 目標位置と実際の位置が同じになったら次のステップに移行
"""

"""
実行して
ESC : 終了
1   : 録画開始．新しい CSV ファイルが作られ，物体位置特定してステップログを保存
2   : 録画終了．CSV ファイルを閉じる．
3   : 動作再現開始．モデルをロードして最初の vp による目標を描画する
"""

DIR_PATH = "tmp/DEMO_result/"

colors = {}
colors["red"   ] = (  0,   0, 255)
colors["blue"  ] = (255,   0,   0)
colors["green" ] = (  0, 255,   0)
colors["yellow"] = (  0, 255, 255)
colors["hand"  ] = (  0,   0,   0)

STOP_RANGE  = 30
STOP_THRESH =  5
 
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

def makeModel():
    stepDict = {}
    logPaths = glob.glob(DIR_PATH + "*")
    for logPath in logPaths:
        logName = os.path.basename(logPath)[:-4]
        stepDict[logName] = []
        with open(logPath, "r", encoding="utf-8") as f:
            tempList = []
            while True:
                line = f.readline().split(",")
                if len(line) < 2:
                    break
                line = np.array([int(float(l)) for l in line[3:-1]])
                # 「直前の状態に対して不変」では，
                # カメラ的にうまくいかない気がするので
                # 後ろのある程度の期間の平均に対して不変 という
                # 方法にしよう

                # 小区間を取得
                if len(tempList) >= STOP_RANGE:
                    tempList.pop(0)
                tempList.append(line)
                    
                # 小区間がたまる前なら無視
                if len(tempList) < STOP_RANGE:
                    continue

 
                # 小区間中の平均を求める
                myu = sum(tempList)/len(tempList) 


                # 分散を求める
                # 平均を引いて転置して内積とれば
                # 対角成分が (x-myu)**2 になる
                # trace とって STOP_RANGE で割れば分散
                t = np.array(tempList)
                var = (t-myu).dot((t-myu).T).trace()/STOP_RANGE
           
                # 分散が閾値未満なら「不変な状態」なので，
                # 平均を取得
                # 直前に取得した平均と不変なら無視  
                if len(stepDict[logName]) == 0:
                    diff = 99999
                else:
                    diff = np.linalg.norm(stepDict[logName][-1]-myu)

                # print("myu:" + str(myu) + "\t\tvar:" + str(var))

                if var < STOP_THRESH and diff > STOP_THRESH:
                    stepDict[logName].append(myu.astype("int"))

    # ここまでで，各ログにおける途中状態を取得できた

    # 一旦表示
    for logName in stepDict.keys():
        for log in stepDict[logName]:
            print(log)

    # 移動した物体をもとにマッチング処理を行う
    # 先生用

    colorDict = {}
    for logName in stepDict.keys():
        b = stepDict[logName][0]
        colorDict[logName] = [[-1, b]]
        for i in range(1, len(stepDict[logName])):
            a = stepDict[logName][i]

            # 前後差が最大となるidxを取得
            c = list((a-b)**2).index(max(list((a-b)**2)))

            # 0,1 -> 赤, 2,3 -> 青, ..., なので
            # 2で割って切り捨てればよさそう
            c = int(c/2)

            colorDict[logName].append([c, a])
            b = a

    # 一旦表示させよう
    for cList in colorDict.keys():
        print(cList)
        for c in colorDict[cList]:
            print(c[0], end=", ")
        print("")

    matchingDict = {}
    for logName in colorDict.keys():
        matchingDict[logName] = [colorDict[logName].pop(0)]

    while True:
        cDict = {}
        for logName in colorDict.keys():
            if colorDict[logName][0][0] not in cDict.keys():
                cDict[colorDict[logName][0][0]]  = 1
            else:
                cDict[colorDict[logName][0][0]] += 1
        
        # 最も多かった色を取得
        c = [c for c in cDict.keys() if cDict[c] == max(cDict.values())][0]

        # この色じゃなかったログを修正
        for logName in colorDict.keys():
            while colorDict[logName][0][0] != c:
                colorDict[logName].pop(0)

        # その色の動作が連続している場合，最後の状態に合わせる
        for logName in colorDict.keys():
            while len(colorDict[logName]) > 1 \
                    and colorDict[logName][1][0] == c:
                colorDict[logName].pop(0)

        # 色がそろったところで matching に保存
        for logName in colorDict.keys():
            matchingDict[logName].append(colorDict[logName].pop(0))

        # colorDict が空になったログがあったら終了
        flag = [len(l) == 0 for l in colorDict.values()]
        flag = reduce((lambda x, y: x or y), flag)
        if flag == True:
            break

    # 一旦表示させよう
    print("---after matching---")
    for cList in matchingDict.keys():
        print(cList)
        for c in matchingDict[cList]:
            print(c[0], end=", ")
        print("")
   
    # ----------ここまでは正しいよライン--------------

    # matchingDict の各ログのステップとインデックスがそろったので，
    # 遷移関数を求める
    # 連立型だと教示が 8 回も必要になっちゃうので，
    # もっと簡単な方法でやろう
    # 動かす物体は既知なので，2式で済むはず？
    # 考えるのが面倒だったので，とりあえず連立型で組んでみよう

    if len(matchingDict.keys()) < 8:
        return 
    selected = list(matchingDict.keys())[:8]
    model = []
    for i in range(len(matchingDict[selected[0]])-1):
        # matchingDict[logName][step][0:color, 1:status]
        before = np.array([matchingDict[s][i][1]   for s in selected])
        after  = np.array([matchingDict[s][i+1][1] for s in selected])
        f      = after.dot(before.T)
        model.append([matchingDict[selected[0]][i+1][0], f])

    # 一旦表示させよう
    print("---model---")
    for m in model:
        print(m[0])
        print(m[1])

    return 

if __name__ == "__main__":
    capture = cv2.VideoCapture(0)

    if os.path.exists(DIR_PATH) == False:
        os.mkdir(DIR_PATH)

    step  = -1
    recFlag = False
    repFlag = False
    debug   = False

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
                logPath = DIR_PATH + "{0:06d}".format(count) + ".csv"
                if os.path.exists(logPath) == False:
                    break
            f = open(logPath, "w", encoding="utf-8")
        elif key == ord("2") and recFlag == True:
            recFlag = False
            f.close()
        elif key == ord("3") and repFlag == False:
            # 動作再現を開始する
            # フラグを立てて matching モデルをロードする
            repFlag = True
            makeModel()
        elif key == ord("4") and repFlag == True:
            repFlag = False
            model = None

        elif key == ord("9"):
            debug = not debug

        _, frame = capture.read()

        # recFlag が立っている場合，物体位置をフレームで囲む
        if recFlag == True:
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
                # text += "0,0,0,0,"
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
