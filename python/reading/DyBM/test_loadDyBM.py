# coding = utf-8

import matplotlib.pyplot as plt
from pydybm.base.generator import NoisySin
from pydybm.time_series.rnn_gaussian_dybm import RNNGaussianDyBM
from pydybm.base.sgd import RMSProp
from sklearn.metrics import mean_squared_error
import soundfile as sf
import numpy as np
import dill

def MSE(y_true,y_pred):
    MSE_each_coordinate = mean_squared_error(y_true,y_pred,multioutput="raw_values")
    return np.sum(MSE_each_coordinate)

def RMSE(y_true,y_pred):
    return np.sqrt(MSE(y_true,y_pred))



print("1")
with open("tmp/dills/3_9.dill", "rb") as f:
    modelf = dill.load(f)
with open("tmp/dills/3_9.dill", "rb") as f:
    modelt = dill.load(f)

print("2")
dataf, samplerate = sf.read("tmp/full.wav")
datat, samplerate = sf.read("tmp/tibetan.wav")
dataf = [np.array(dataf[i]) for i in range(len(datat))]
datat = [np.array(datat[i]) for i in range(len(datat))]
print("3")

errorListf = []
errorListt = []
i = 0
j = 1000
# modelf.init_state()
# modelt.init_state()
while i+j < min(len(dataf), len(datat)):
    i += j
    predf = modelf.get_predictions(dataf[i:i+j])
    # predf = modelf.learn(dataf[i:i+j])
    predt = modelt.get_predictions(datat[i:i+j])
    # predt = modelt.learn(datat[i:i+j])
    errorListf.append(RMSE(dataf[i:i+j], predf))
    # errorListf.append(RMSE(predf["actual"], predf["prediction"]))
    errorListt.append(RMSE(datat[i:i+j], predt))
    # errorListt.append(RMSE(predt["actual"], predt["prediction"]))
    print(str(errorListf[-1])+":"+str(errorListt[-1]))
    # exit()
    plt.title("RMSE")
    plt.ylim((0, 0.1))
    plt.plot(errorListf[max(0, len(errorListf)-100):], label="full")
    plt.ylim((0, 0.1))
    plt.plot(errorListt[max(0, len(errorListt)-100):], label="tibetan")
    plt.legend()
    plt.pause(0.001)
    plt.clf()
