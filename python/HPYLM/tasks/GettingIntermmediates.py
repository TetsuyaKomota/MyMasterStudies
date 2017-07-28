#-*- coding: utf-8 -*-

import dill
import Restaurant

# HPYLM_results.dill と HMM_results_naive.dill から，
# 単語境界のステップ数を取得する

# HPYLM の結果のパス
RES_PATH_HPYLM     = "tmp/log_MakerMain/dills/HPYLM_results.dill"
# 縮約前の HMM の符号化結果のパス
RES_PATH_HMM_NAIVE = "tmp/log_makerMain/dills/HMM_results_naive.dill"

# それぞれ読み込む
with open(RES_PATH_HPYLM, "rb") as f:
    datas_HPYLM = dill.load(f)
with open(RES_PATH_HMM_NAIVE, "rb") as f:
    datas_HMM_naive = dill.load(f)

# HMM_results_naive.dill は数字列のままなので
# Restaurant の translate を使って符号化する

rest = Restaurant.Restaurant(None, [])
u = {}
for d in datas_HMM_naive:
    line = ""
    for s in datas_HMM_naive[d]:
        line = line + rest.translate(s)
    u[d] = line
datas_HMM_naive = u

# 境界部分のステップ番号のリストを作る
output = {}

# HPYLM の結果が dict でなく list なので，
# for 文のインデックスを昇順に渡すよう配慮する必要がある
l = list(datas_HMM_naive)
l.sort()
for i, d in enumerate(l):
    print(d)
    m = []
    naive = datas_HMM_naive[d]
    sentense = datas_HPYLM[i]
    step = 0
    for word in sentense:
        for c in word:
            while True:
                if naive[step] == c:
                    step = step + 1
                else:
                    break
        m.append(step)
    output[d] = m
# とりあえず表示してみる
print(output)
