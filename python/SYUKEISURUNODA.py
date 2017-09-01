#-*- coding: utf-8 -*-

# KOREDEIINODA のぶんまわしで生成した各ディレクトリの結果をまとめる

import glob
import os
import matplotlib.pyplot as plt

root = "tmp/log_MakerMain/GettingIntermediated/"
# 対象のディレクトリ一覧を取得
# GettingIntermediated にあるすべてのディレクトリ
dirs = []
for g in glob.glob(root + "*"):
    # print(g)
    if os.path.isdir(g):
        dirs.append(os.path.basename(g) + "/")
# print(dirs)
# 対象のファイル名一覧を取得
# 各ディレクトリのファイル構成は同じはず
files = []
for g in glob.glob(root + dirs[0] + "*"):
    # print(g)
    files.append(os.path.basename(g))
# print(files)
# print(len(files))

# 学習した動作の最大ステップ数を取得
# 最終状態は途中上代に含めているはずなので，
# 途中状態ファイルの最後のログのステップ数を見ればいいはず
maxstep = 0
with open(root + dirs[1] + files[0], "r", encoding = "utf-8") as f:
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
        with open(root + d + f, "r", encoding = "utf-8") as csv:
            while True:
                line = csv.readline().split(",")[0]
                if line == "":
                    break
                hist[int(line)] += 1
                bag.append(int(line))
    output[d] = hist
    bags[d] = bag

# 書き出し先のディレクトリが存在しないなら作る
# surface で動かしたときにエラーにならないように
if not os.path.exists("tmp/SYUKEISURUNODA_results/"):
    os.mkdir("tmp/SYUKEISURUNODA_results")
# ヒストグラムの png を生成する
for b in bags:
    plt.hist(bags[b], bins = 250)
    plt.savefig("tmp/SYUKEISURUNODA_results/" + b[:-1] + ".png")
    plt.close()
    # plt.figure()
# csv 書き出し
# print(output)
outlist = sorted(list(output.keys()))
with open("tmp/SYUKEISURUNODA_results/results.csv", "w", encoding="utf-8") as f:
    for l in outlist:
        f.write(l + ",")
        for o in output[l]:
            f.write(str(o) + ",")
        f.write("\n")
