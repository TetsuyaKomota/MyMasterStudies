#-*- coding: utf-8 -*-

import copy
import numpy as np

# GetIntermmediates.py で取得した途中状態のデータに対して
# 観点変換を行う

# ログの文字列を引数に，使いやすいように変換
def encodeState(line):
    # ログデータは最後にカンマがついているので
    # temp[-1]は \n のみ
    temp = line.split(",")
    if len(temp) != 32:
        print("[ViewPointEncoder]encodeState:invalid input :"+line)
        return None
    output = {}
    output["step"  ] = int(temp[0])
    output["hand"  ] = np.array([float(i) for i in temp[1:3]])
    output["red"   ] = np.array([float(i) for i in temp[7:9]])
    output["blue"  ] = np.array([float(i) for i in temp[13:15]])
    output["green" ] = np.array([float(i) for i in temp[19:21]])
    output["yellow"] = np.array([float(i) for i in temp[25:27]])
    return output

def decodeState(state):
    line = ""
    line = line + str(state["step"])+","
    line = line + str(list(state["hand"  ]))[1:-1]+","
    line = line + str(list(state["red"   ]))[1:-1]+","
    line = line + str(list(state["blue"  ]))[1:-1]+","
    line = line + str(list(state["green" ]))[1:-1]+","
    line = line + str(list(state["yellow"]))[1:-1]+","
    return line

def serialize(state):
    output = []
    output = output + [state["timelen"]]
    output = output + list(state["hand"  ])
    output = output + list(state["red"   ])
    output = output + list(state["blue"  ])
    output = output + list(state["green" ])
    output = output + list(state["yellow"])
    return output

# 状態，基準物体，参照点を引数に，変換した状態を返す
# 複数の場合は重心を参照する
def transformforViewPoint(state, baseList, refList, smax=1000, scale=20000):
    # とりあえずコピー
    output = copy.deepcopy(state)
    del output["step"]
    # base, ref を求める
    base = np.zeros(2)
    for b in baseList:
        base = base + state[b]
    if len(baseList) > 0:
        base = base / len(baseList)
    ref = np.zeros(2)
    for r in refList:
        ref  = ref  + state[r]
    if len(refList)  > 0:
        ref  = ref  / len(refList)
    # ref をbase 中心に変換する
    ref = ref - base
    # 回転角を求める
    theta = np.arctan(ref[1]/ref[0])
    if ref[0] < 0:
        theta = theta + np.pi
    # 回転行列を作る
    if len(refList) == 0:
        rot = np.eye(2)
    else:
        rot = np.array([[np.cos(theta), np.sin(theta)], [-1*np.sin(theta), np.cos(theta)]])
    # 平行移動,回転させる
    for t in output:
        output[t] = rot.dot(output[t] - base)
    # 最後にステップの情報を変換してくっつける
    output["step"] = state["step"]
    output["timelen"] = (state["step"]/smax)*scale
    return output

if __name__ == "__main__":
    line = "1,"
    line = line + "1,1,0,0,0,0,"
    line = line + "2,2,0,0,0,0,"
    line = line + "0,2,0,0,0,0,"
    line = line + "0,-3,0,0,0,0,"
    line = line + "0,0,0,0,0,0,"
    b = encodeState(line)
    # a = transformforViewPoint(b, ["hand"], ["red"])
    a = transformforViewPoint(b, ["blue"], ["hand"])
    print(b)
    print(a)
    de = decodeState(a)
    print(de)
    se = serialize(a)
    print(se)
