# coding = utf-8

# 物体移動の認識程度であれば，キネクトなんて使わないで
# カメラと OpenCV で何とかなることに気づいてしまった

import cv2
import copy
import numpy as np

# 指定した色の物体の位置を返す
def capture(inputImg, color):
    img = copy.deepcopy(inputImg)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV_FULL)
    h = hsv[:, :, 0]
    s = hsv[:, :, 1]

    mask = np.zeros(h.shape, dtype=np.uint8)
    mask[((h < 20) | (h > 200)) & (s > 128)] = 255
    _, contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    rects = []
    for contour in contours:
        approx = cv2.convexHull(contour)
        rect = cv2.boundingRect(approx)
        rects.append(np.array(rect))
    if len(rects) > 0:
        rect = max(rects, key=(lambda x: x[2] * x[3]))
        cv2.rectangle(img, tuple(rect[0:2]), tuple(rect[0:2] + rect[2:4]), (0, 0, 255), thickness=2)

    # 表示してみる
    cv2.imshow('red', img) 
    cv2.waitKey(0)
    # 重心をとる
    return 0

if __name__ == "__main__":
    img = cv2.imread("tmp/1.PNG")
    capture(img, 0)
