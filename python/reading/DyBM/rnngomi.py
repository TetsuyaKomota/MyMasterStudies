import matplotlib.pyplot as plt
from pydybm.base.generator import NoisySin
from pydybm.time_series.rnn_gaussian_dybm import RNNGaussianDyBM
from pydybm.base.sgd import RMSProp
from sklearn.metrics import mean_squared_error
import soundfile as sf
import numpy as np

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
data, samplerate = sf.read("tmp/kemono_op.wav")
timeSeries = []
for i in range(int(len(data)/3), (len(data))):
    timeSeries.append(np.array(data[i]))

#DyBM initialization parameters
in_dim = 2        # dimension of the input time-series
out_dim = 2       # dimension of the expected output time-series
rnn_dim = 100     # dimension of RNN layer
max_iter =  1     # maximum number of learning epochs/iterations to run
SGD = RMSProp     # setting the SGD optimization method  

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
for i in range(max_iter):
    #initialize the memory units in DyBM
    model.init_state() 
    #learn the time-series patterns and return the predicted and actual data
    result= model.learn(timeSeries, get_result=True)
    #calculate the prediction error
    error = RMSE(result["actual"],result["prediction"])
    print ('Learning epoch RMSE : %.5f' %(error))

# sf.write("tmp/kemono_002.wav", [r[0] for r in result["prediction"]], samplerate)
sf.write("tmp/kemono_002.wav", result["prediction"], samplerate)

plt.subplot(2, 1, 1)
plt.title("First 900")
plt.plot([a[0] for a in result["actual"]][:900],label="target")
plt.plot([a[0] for a in result["prediction"]][:900],label="prediction")
plt.legend()
plt.subplot(2, 1, 2)
plt.title("Last  900")
plt.plot([a[0] for a in result["actual"]][-900:],label="target")
plt.plot([a[0] for a in result["prediction"]][-900:],label="prediction")
plt.legend()
plt.show()
    

# _update_state という内部メソッドが怪しい
# time_series_model の get_prediction の実装見ると
# こんな感じで行けそう
# model.init_state()
tRange = 10
for t, tRate in enumerate([2**i for i in range(tRange)]):
    gen = [timeSeries[0]]
    model.init_state()
    for i in range(len(timeSeries)):
        pred = model.predict_next()
        gen.append(pred)
        print(pred)
        if i%tRate == 0:
            model._update_state(timeSeries[i])
        else:
            model._update_state(pred)
    plt.subplot(tRange, 1, t+1)
    plt.title("True data in each " + str(tRate) + "step")
    plt.plot([g[0] for g in gen][:900],label="generated")
    plt.legend()
    # sf.write("tmp/kemono_004_"+str(tRate)+".wav", [g[0] for g in gen], samplerate)
    sf.write("tmp/kemono_004_"+str(tRate)+".wav", gen, samplerate)

plt.show()
"""
gen = [timeSeries[0]]
for i in range(int(len(timeSeries)/2)):
    model.init_state()
    result = model.learn(gen, get_result=True)

    print(result["prediction"][-1])
    gen.append(result["prediction"][-1])
plt.plot(result["actual"],label="target")
plt.plot(result["prediction"],label="prediction")
plt.legend()
plt.show()

sf.write("tmp/003.wav", [g[0] for g in gen], samplerate)
"""
