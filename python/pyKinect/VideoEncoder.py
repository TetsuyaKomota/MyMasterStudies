# coding = utf-8
import cv2
import numpy as np
import os

"""
実行して
ESC : 終了
1   : 録画開始．新しい CSV ファイルが作られ，物体位置特定してステップログを保存
2   : 録画終了．CSV ファイルを閉じる．
"""

def find_rect_of_target_color(image, color):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV_FULL)
    h = hsv[:, :, 0]
    s = hsv[:, :, 1]
    mask = np.zeros(h.shape, dtype=np.uint8)
    if color == "red":
        mask[((h < 5) | (h > 210)) & (s > 200)] = 255
    elif color == "blue":
        mask[((h > 150) & (h < 180)) & (s > 200)] = 255
    elif color == "green":
        mask[((h > 60) & (h < 130)) & (s > 128)] = 255
    elif color == "yellow":
        mask[((h > 30) & (h < 60)) & (s > 200)] = 255
    elif color == "hand":
        # mask[(s < 10)] = 255
        mask[(s < 0)] = 255
    _, contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    rects = []
    for contour in contours:
        approx = cv2.convexHull(contour)
        rect = cv2.boundingRect(approx)
        rects.append(np.array(rect))
    return rects

if __name__ == "__main__":
    colors = {}
    colors["red"]    = (0, 0, 255)
    colors["blue"]   = (255, 0, 0)
    colors["green"]  = (0, 255, 0)
    colors["yellow"] = (0, 255, 255)
    colors["hand"]   = (0, 0, 0)
    capture = cv2.VideoCapture(0)
    if os.path.exists("tmp/VideoEncoder_results") == False:
        os.mkdir("tmp/VideoEncoder_results")
    count = 0
    recFlag = False
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
            while True:
                count += 1
                if os.path.exists("tmp/VideoEncoder_results/"+"{0:06d}".format(count) + ".csv") == False:
                    break
            f = open("tmp/VideoEncoder_results/"+"{0:06d}".format(count) + ".csv", "w", encoding="utf-8")
        elif key == ord("2") and recFlag == True:
            recFlag = False
            f.close()
        elif key == ord("9"):
            debug = not debug


        _, frame = capture.read()
        
        if recFlag == True:
            step += 1
            text = str(step) + ","
            # ログの順番を指定するために colors.keys() ではなくこの形
            for c in ["hand", "red", "blue", "green", "yellow"]:
                rects = find_rect_of_target_color(frame, c)
                if len(rects) > 0:
                    rect = max(rects, key=(lambda x: x[2] * x[3]))
                else:
                    rect = [0, 0, 0, 0]
                if rect[2] * rect[3] > 1000:
                    cv2.rectangle(frame, tuple(rect[0:2]), tuple(rect[0:2] + rect[2:4]), colors[c], thickness=2)
                else:
                    rect = [0, 0, 0, 0]
                
                # TODO ここからいらない
                if debug == True:
                    if c == "red":
                        red = rect
                    if c == "yellow":
                        yellow = rect
                    if np.linalg.norm(red) != 0 and np.linalg.norm(yellow) != 0:
                        newblue = np.array([2*(yellow[0])-red[0], 2*(yellow[1])-red[1], red[2], red[3]])
                        cv2.rectangle(frame, tuple(newblue[0:2]), tuple(newblue[0:2] + np.array([50, 50])), (255, 100, 100), thickness=2)
                # TODO ここまでいらない
 
                text += (str(rect[0]+rect[2]/2)+",")
                text += (str(rect[1]+rect[3]/2)+",")
                text += "0,0,0,0,"
            f.write(text + "\n") 
        cv2.imshow('red', frame)
    capture.release()
    f.close()
    cv2.destroyAllWindows()
