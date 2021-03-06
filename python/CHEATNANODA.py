# coding = utf-8

# HPYLM で超きれいに形態素解析できたら，のファイルを生成するプログラム

import random

import glob

import os

fpaths = glob.glob("tmp/log_MakerMain/*")
result = "tmp/CHEATNANODA_results/"

if os.path.exists(result) == False:
    os.mkdir(result)

for fpath in fpaths:
    if fpath[-4:] != ".csv":
        continue
    with open(fpath, "r", encoding="utf-8") as f:
        with open(result + "inter" + os.path.basename(fpath)[3:], "w", encoding="utf-8") as g:
            count = 0
            dev  = 0
            rand = int(random.random()*4)-2
            while True:
                line = f.readline()
                if line == "":
                    break
                count += 1
                if dev == 0 or count == 499 or count == dev*100 + rand:
                    # 境界が検出されない状態を生成
                    if False and random.random() < 0.3:
                        dev += 1
                    else:
                            rand = int(random.random()*10)-5
                            dev += 1
                            g.write(line) 
