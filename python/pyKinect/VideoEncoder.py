# coding = utf-8
import cv2
import numpy as np
import os

def find_rect_of_target_color(image, color):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV_FULL)
    h = hsv[:, :, 0]
    s = hsv[:, :, 1]
    mask = np.zeros(h.shape, dtype=np.uint8)
    if color == "red":
        mask[((h < 10) | (h > 210)) & (s > 128)] = 255
    elif color == "blue":
        mask[((h > 160) & (h < 210)) & (s > 128)] = 255
    elif color == "green":
        mask[((h > 60) & (h < 130)) & (s > 128)] = 255
    elif color == "yellow":
        mask[((h > 10) & (h < 60)) & (s > 128)] = 255
    elif color == "black":
        mask[(s < 10)] = 255
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
    colors["black"]  = (0, 0, 0)
    capture = cv2.VideoCapture(0)
    if os.path.exists("tmp/VideoEncoder_results") == False:
        os.mkdir("tmp/VideoEncoder_results")
    count = 0
    while True:
        count += 1
        if os.path.exists("tmp/VideoEncoder_results/"+"{0:06d}".format(count) + ".csv") == False:
            break
    f = open("tmp/VideoEncoder_results/"+"{0:06d}".format(count) + ".csv", "w", encoding="utf-8")
    while cv2.waitKey(30) < 0:
        _, frame = capture.read()
        text = ""
        for c in colors.keys():
            rects = find_rect_of_target_color(frame, c)
            if len(rects) > 0:
                rect = max(rects, key=(lambda x: x[2] * x[3]))
            else:
                rect = [0, 0, 0, 0]
            if rect[2] * rect[3] > 10000:
                cv2.rectangle(frame, tuple(rect[0:2]), tuple(rect[0:2] + rect[2:4]), colors[c], thickness=2)
            else:
                rect = [0, 0, 0, 0]
            text += (str(rect[0]+rect[2]/2)+",")
            text += (str(rect[1]+rect[3]/2)+",")
        cv2.imshow('red', frame)
        f.write(text + "\n") 
    capture.release()
    f.close()
    cv2.destroyAllWindows()
