import matplotlib.pyplot as plt
from pydybm.base.generator import NoisySin
from pydybm.time_series.rnn_gaussian_dybm import RNNGaussianDyBM
from pydybm.base.sgd import RMSProp
from sklearn.metrics import mean_squared_error
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

# Prepare a generator of noisy sine wave time-series
length = 60000  # length of the time-series
period = 80   # period of the sine wave
std = 0.1     # standard deviation of the noise
dim = 1       # dimension of the time-series
timeSeries = NoisySin(length,period,std,dim)


#DyBM initialization parameters
in_dim = 1        # dimension of the input time-series
out_dim = 1       # dimension of the expected output time-series
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
    #reset the noisey sine wave time series data
    timeSeries.reset(i)
    #learn the time-series patterns and return the predicted and actual data
    result= model.learn(timeSeries, get_result=True)
    #calculate the prediction error
    error = RMSE(result["actual"],result["prediction"])
    print ('Learning epoch RMSE : %.5f' %(error))
    
# Plot the time-series and prediction 

plt.subplot(2, 1, 1)
plt.title("First 900 step")
plt.plot(result["actual"][:900],label="target")
plt.plot(result["prediction"][:900],label="prediction")
plt.legend()
plt.subplot(2, 1, 2)
plt.title("Last  900 step")
plt.plot(result["actual"][-900:],label="target")
plt.plot(result["prediction"][-900:],label="prediction")
plt.legend()
plt.show()
