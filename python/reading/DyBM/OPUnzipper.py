# coding = utf-8

import matplotlib.pyplot as plt
from pydybm.base.generator import NoisySin
from pydybm.time_series.rnn_gaussian_dybm import RNNGaussianDyBM
from pydybm.base.sgd import RMSProp
from sklearn.metrics import mean_squared_error
import soundfile as sf
import numpy as np
import dill

# OPZipper で超圧縮したけものフレンズOP を展開する

# 正解データを取得する
data, samplerate = sf.read("tmp/kemono_op.wav")
timeSeries = []
for i in range(len(data)):
    timeSeries.append(np.array(data[i]))

# 圧縮モデルをロード
with open("tmp/dills/zipped.dill", "rb") as f:
    model = dill.load(f)

# OP をデコード
# init_state なしに predict_next を実行する
# dump の時点で OP を(2 period)入れてあるはずなので，
# そのまま次を要求すれば最初から取得できるはず
decodedList = []
for i in range(len(data)):
    decodedList.append(model.predict_next())
    model._update_state(decodedList[-1])
    # print(decodedList[-1])

# 音声ファイルに出力
sf.write("tmp/unzipped.wav", decodedList, samplerate)
