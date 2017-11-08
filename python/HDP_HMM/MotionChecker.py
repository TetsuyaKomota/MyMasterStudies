# coding = utf-8

# log データを可視化してチェックするだけ

import glob
import os
import HDP_HMM.MakerMain as makerMain
import DPM.ViewPointEncoder as encoder
import DPM.ViewPointManager as manager

fpaths = glob.glob("tmp/log_MakerMain/*")

for fpath in fpaths:
    if os.path.basename(fpath)[:3] != "log" \
            or fpath[-4:] != ".csv":
        continue
    if int(os.path.basename(fpath)[-6:-4]) > 2:
        continue
    with open(fpath, "r", encoding="utf-8") as f:
        count = 0
        while True:
            line = f.readline()
            if line == "":
                break
            if count%100 == 0:
                manager.show(encoder.encodeState(line), title=fpath)
            count += 1
