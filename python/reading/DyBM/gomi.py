import matplotlib.pyplot as plt
# from pydybm.time_series.dybm import LinearDyBM
from pydybm.time_series.rnn_gaussian_dybm import RNNGaussianDyBM
from pydybm.base.generator import NoisySin
from pydybm.base.generator import SequenceGenerator
import soundfile as sf
import numpy as np


# Prepare a generator of time-series
# In this example, we generate a noisy sine wave
length = 300000 # length of the time-series
period = 60  # period of the sine wave
std = 0.1   # standard deviation of the noise
dim = 1      # dimension of the time-series

data, samplerate = sf.read("702.wav")
dataw,samplerate = sf.read("801.wav")
datav,samplerate = sf.read("901.wav")
in_data = NoisySin(int(len(data)/2),period,std,dim)
X = []
y = []
w = []
v = []
v = [np.array([0]) for i in range(len(data))]
for i in range(int(len(data)/1)):
    X.append(np.array([data[i]]))
    w.append(np.array([dataw[i]]))
#     v.append(np.array([datav[i]]))
    if len(X) >= 2:
        y.append(np.array(X[-1]-X[-2]))
y.append(y[-1])
# Create a DyBM
# In this example, we use the simplest Linear DyBM
# dybm = LinearDyBM(dim)
dybm = RNNGaussianDyBM(dim)

# Learn and predict the time-series in an online manner
# result = dybm.learn(data)
for _ in range(10):
        result = dybm.learn(SequenceGenerator(X), SequenceGenerator(w))
        dybm.init_state()
        result = dybm.learn(SequenceGenerator(w), SequenceGenerator(X))
        dybm.init_state()
# result = dybm.learn(SequenceGenerator(X))

"""
z = [X[0]]
in_data = NoisySin(int(len(data)/4),period,std,dim)
dybm.init_state()
for i in range(int(len(data)/4)):
    # z.append(dybm.learn(z)["prediction"][-1])
    dybm.learn_one_step(z[-1])
    z.append(z[-1]+dybm.predict_next())
"""
# z = dybm.get_predictions(SequenceGenerator(X))
z = dybm.get_predictions(SequenceGenerator(w))
u = dybm.get_predictions(SequenceGenerator(v))

z = [zi[0] for zi in z]
z = np.array(z)
u = [ui[0] for ui in u]
u = np.array(u)
# sf.write("704.wav", z, samplerate)
sf.write("802.wav", z, samplerate)
sf.write("902.wav", u, samplerate)

# Plot the time-series and prediction
plt.subplot(4, 1, 1)
plt.title("First 900 step")
plt.plot(result["actual"][:900],label="target")
plt.plot(result["prediction"][:900],label="prediction")
plt.legend()

plt.subplot(4, 1, 2)
plt.title("Last 900 step")
plt.plot(result["actual"][-900:],label="target")
plt.plot(result["prediction"][-900:],label="prediction")
plt.legend()

plt.subplot(4, 1, 3)
plt.title("Generated 900 step")
plt.plot(w[-900:],label="target")
plt.plot(z[-900:],label="generated")
plt.legend()

plt.subplot(4, 1, 4)
plt.title("Generated 900 step")
plt.plot(v[-900:],label="target")
plt.plot(u[-900:],label="generated")
plt.legend()


plt.show()

y = []
for d in result["prediction"]:
    y.append(d[0])
y = np.array(y)
sf.write("703.wav", y, samplerate)


