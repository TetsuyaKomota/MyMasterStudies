#-*- coding: utf-8 -*-

import math
import glob
import numpy as np


# MakerMotions で生成した時系列データに後処理を加える

# ファイルを読み込む
def inputData(filepath):
    output = []
    with open(filepath, "r") as f:
        while(True):
            line = f.readline().split(",")[:-1]
            if len(line) < 2:
                break
            output.append([float(x) for x in line])
    return output

# ファイルを書きだす
def outputData(output, filepath):
    post_path = "tmp/log_MakerMain/PostProcessed/post_"
    with open(post_path+filepath[-12:], "w") as f:
        for o in output:
            line = ""
            for d in o:
                line = line + str(d) + ","
            line = line + "\n"
            f.write(line)

# hand の情報のみに変換
def getHandData(datas):
    output = []
    for d in datas:
        output.append([d[1], d[2]])
    return output

# 取得したデータを単純移動平均で平滑化
# 前後 length の平均をとるので，範囲は 2*length
# 両端のデータはそれぞれ片側の平均しか取れない(取らない)
def getSMAList(datas, length=10):
    output = []
    # バッファ．こいつに足したり引いたりする
    buf = np.zeros(len(datas[0]))
    # バッファに保持されているデータの数
    count = 0
    # まず右側の平均を取得する
    for l in range(length+1): # 自分を含めるために +1
        if len(datas) > l:
            count = count + 1
            buf = buf + np.array(datas[l])
        else:
            break
    # 移動平均を計算する
    for idx in range(len(datas)):
        # データを取得する
        output.append(buf/count)
        # 移動する
        # 現在のデータは次のデータの左側となるので，加える
        # count = count + 1
        # buf = buf + datas[idx]
        # 左側のデータ数が既にlength 個あるなら，移動する際に一つ取り除く
        if idx >= length:
            count = count - 1
            buf = buf - np.array(datas[idx-length])
        # 右側のデータ数が length 以上ある場合は buf に加える
        # idx+length までは含まれているから，その次ということで +1
        if idx+length+1 < len(datas):
            count = count + 1
            buf = buf + np.array(datas[idx+length+1])
    return output 

# 取得したデータを三角移動平均で平滑化
def getTMAList(datas, length=10):
    output = []
    half_length = math.ceil((length+1)/2)
    output = getSMAList(getSMAList(datas, half_length), half_length)
    return output

# 取得したデータを速度列に変換
def getVelocityList(datas, timeDelta=0.01):
    output = []
    prev = np.array(datas[0])
    for d in datas[1:]:
        output.append((np.array(d)-prev)/timeDelta)
        prev = d
    # 長さを datas と合わせる
    output.append(output[-1])
    return output

if __name__ == "__main__":
    filepaths = glob.glob("tmp/log_MakerMain/*")
    for p in filepaths:
        print(p)
        if p[-4:] != ".csv":
            continue
        output = inputData(p)
        output = getHandData(output)
        output = getTMAList(output)
        output = getVelocityList(output)
        outputData(output, p)
    print("Successfuly PostProcessed")
