import matplotlib.pyplot as plt
from pydybm.base.generator import NoisySin
from pydybm.time_series.rnn_gaussian_dybm import RNNGaussianDyBM
from pydybm.base.sgd import RMSProp
from sklearn.metrics import mean_squared_error
import soundfile as sf
import numpy as np
import dill

# けものフレンズじゃない音声が聞こえてきたら識別する DyBM

def MSE(y_true,y_pred):
    """
    Function to calculate the mean squared error of a sequence of predicted vectors
    
    y_true : array, shape(L,N)
    y_pred : array, shape(L,N)

    mean of (dy_1^2 + ... + dy_N^2 ) over L pairs of vectors (y_true[i],y_pred[i])
    """
    MSE_each_coordinate = mean_squared_error(y_true,y_pred,multioutput="raw_values")
    return np.sum(MSE_each_coordinate)

def RMSE(y_true,y_pred):
    """
    Function to calculate the root mean squared error of a sequence of predicted vectors
    
    y_true : array, shape(L,N)
    y_pred : array, shape(L,N)

    squared root of the mean of (dy_1^2 + ... + dy_N^2 ) over L pairs of vectors (y_true[i],y_pred[i])
    """
    return np.sqrt(MSE(y_true,y_pred))

# data, samplerate = sf.read("tmp/001.wav")
# data, samplerate = sf.read("tmp/merged.wav")
data, samplerate = sf.read("tmp/full.wav")
timeSeries = []
for i in range(int(len(data)/3), (len(data))):
    timeSeries.append(np.array(data[i]))

#DyBM initialization parameters
in_dim    =   2     # dimension of the input time-series
out_dim   =   2     # dimension of the expected output time-series
rnn_dim   = 100     # dimension of RNN layer
max_iter  =  10     # maximum number of learning epochs/iterations to run
batch_num =  10 
SGD = RMSProp       # setting the SGD optimization method  

#setting RNN-G-DyBM hyperparameters
delay = 2
decay = 0.3
sparsity = 0.1
spectral_radius = 0.95
leak = 1.0
learning_rate = 0.001
random_seed = 2

# Create and initialize a RNN-Gaussian DyBM
model = RNNGaussianDyBM(in_dim,out_dim,rnn_dim,spectral_radius,sparsity,delay=delay,
                        decay_rates =[decay],leak=leak, random_seed = random_seed, SGD=SGD())  
model.set_learning_rate(learning_rate)


#training the RNNGaussian DyBM
batch_size = int(len(timeSeries)/batch_num)
for i in range(max_iter):
    for j in range(batch_num):
        #initialize the memory units in DyBM
        model.init_state() 
        #learn the time-series patterns and return the predicted and actual data
        result = model.learn(timeSeries[batch_size*j:batch_size*(j+1)], get_result=True)
        #calculate the prediction error
        error  = RMSE(result["actual"],result["prediction"])
        print("Learning epoch: %d-%d RMSE: %.5f" %(i, j, error))
        with open("tmp/dills/"+str(i)+"_"+str(j)+".dill", "wb") as f:
            dill.dump(model, f)

errorList = []
for i in range(len(result["actual"])):
    errorList.append(np.linalg.norm(result["actual"][i]-result["prediction"][i]))

errorIdx = errorList.index(max(errorList[1000:]))

plt.subplot(3, 1, 1)
plt.title("First 900")
plt.plot([a[0] for a in result["actual"]][:900],label="target")
plt.plot([a[0] for a in result["prediction"]][:900],label="prediction")
plt.plot(errorList[:900],label="error")
plt.legend()
plt.subplot(3, 1, 2)
plt.title("Inter 900")
inter = errorIdx
print("length="+str(len(data)))
print("inter="+str(inter))
plt.plot([a[0] for a in result["actual"]][inter-450:inter+450],label="target")
plt.plot([a[0] for a in result["prediction"]][inter-450:inter+450],label="prediction")
plt.plot(errorList[inter-450:inter+450],label="error")
plt.legend()
plt.subplot(3, 1, 3)
plt.title("Last  900")
plt.plot([a[0] for a in result["actual"]][-900:],label="target")
plt.plot([a[0] for a in result["prediction"]][-900:],label="prediction")
plt.plot(errorList[-900:],label="error")
plt.legend()
plt.show()

# けもフレ警察に引っかかった部分を音声ファイル化
# sf.write("tmp/picked_by_kemoPolice.wav", data[inter-150000:inter+150000], samplerate)
