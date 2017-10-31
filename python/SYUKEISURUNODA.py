#-*- coding: utf-8 -*-

# KOREDEIINODA のぶんまわしで生成した各ディレクトリの結果をまとめる

import glob
import os
import matplotlib.pyplot as plt

root_in  = "tmp/log_MakerMain/GettingIntermediated/"
root_out = "tmp/SYUKEISURUNODA_results/"

# 対象のディレクトリ一覧を取得
# GettingIntermediated にあるすべてのディレクトリ
dirs = []
for g in glob.glob(root_in + "*"):
    # print(g)
    if os.path.isdir(g):
        dirs.append(os.path.basename(g) + "/")
# print(dirs)
# 対象のファイル名一覧を取得
# 各ディレクトリのファイル構成は同じはず
files = []
for g in glob.glob(root_in + dirs[0] + "*"):
    # print(g)
    files.append(os.path.basename(g))
# print(files)
# print(len(files))

# 学習した動作の最大ステップ数を取得
# 最終状態は途中状態に含めているはずなので，
# 途中状態ファイルの最後のログのステップ数を見ればいいはず
maxstep = 0
with open(root_in + dirs[0] + files[0], "r", encoding = "utf-8") as f:
    while True:
        line = f.readline().split(",")[0]
        if line == "":
            break
        maxstep = int(line)
print("maxstep:" + str(maxstep))

# 集計をとる
# output は csv ファイルにする用でカウンティング済みの物
# bags は plt のヒストグラムを書く用で，ただ突っ込んだもの
output = {}
bags = {}
for d in dirs:
    hist = [0 for _ in range(maxstep + 1)]
    bag = []
    for f in files:
        with open(root_in + d + f, "r", encoding = "utf-8") as csv:
            while True:
                line = csv.readline().split(",")[0]
                if line == "":
                    break
                hist[int(line)] += 1
                bag.append(int(line))
    # 集計の関係上，各パラメータごとに分けたタプルをキーとする
    dTuple = tuple(d[:-1].split("-"))
    output[dTuple] = hist
    bags[dTuple] = bag

# 書き出し先のディレクトリが存在しないなら作る
# surface で動かしたときにエラーにならないように
if not os.path.exists(root_out):
    os.mkdir(root_out)
# ヒストグラムの png を生成する
for b in bags:
    plt.hist(bags[b], bins = 250)
    plt.savefig(root_out + "-".join(b) + ".png")
    plt.close()
    # plt.figure()
# csv 書き出し
# print(output)
outlist = sorted(list(output.keys()))
with open(root_out + "results.csv", "w", encoding="utf-8") as f:
    for l in outlist:
        # タプルをもとに戻してから出力
        f.write("-".join(dTuple) + ",")
        for o in output[l]:
            f.write(str(o) + ",")
        f.write("\n")

# 各パラメータごとの統計を求めてみる
numofParam = len(list(output.keys())[0])
for pIdx in range(numofParam):
    # そのパラメータの変位(範囲)を取得する
    pRange = set([o[pIdx] for o in output.keys() if len(o) == numofParam])
    # 変化しないパラメータは無視
    if len(pRange) <= 1:
        continue
    with open(root_out+"Param"+str(pIdx)+".csv", "w",encoding="utf-8") as f:
        # パラメータの種類ごとに csv を作成
        # パラメータの値ごとに統計とって行で出力
        for p in pRange:
            temp = [output[dt] for dt in output.keys() if len(dt) == numofParam and dt[pIdx]==p] 
            resofP = []
            for step in range(len(temp[0])):
                resofP.append(0)
                for t in temp:
                    resofP[-1] += t[step]
                resofP[-1] = str(resofP[-1])
            f.write(str(p) + ",")
            f.write(",".join(resofP))
            f.write("\n")
