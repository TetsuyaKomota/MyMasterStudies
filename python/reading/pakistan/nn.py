# coding = utf-8 

# 推定結果 [ 33.27183857  70.68814482] に最も近い過去のデータを探す

import numpy as np

pre = np.array([ 33.27183857, 70.68814482])

NN = np.zeros(2)
tempmin = 100000
with open("tmp/are.csv", "r", encoding="utf-8") as f:
    count = 0
    while True:
        line = f.readline()[:-1].split(",")
        count += 1
        print(count)
        if len(line) < 2:
            break
        point = np.array([float(line[2]), float(line[3])])
        if np.linalg.norm(pre-point) < tempmin:
            tempmin = np.linalg.norm(pre-point)
            NN = point
print(NN)
        
