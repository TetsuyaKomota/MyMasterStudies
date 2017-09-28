#-*- coding: utf-8 -*-

from sklearn import mixture
import dill
import matplotlib.pyplot as plt
import dill
import scipy.io

model = mixture.BayesianGaussianMixture(n_components = 10, n_init=150, weight_concentration_prior=0.1)

# data = scipy.io.loadmat("Inputdata.mat")["Inputsample"]
# data = scipy.io.loadmat("TrainingSamples.mat")["Inputsample"]
data = scipy.io.loadmat("TrainingSamples.mat")["Signals"]
# with open("tmp/log_MakerMain/dills/test_pov.dill", "rb") as f:
#     data = dill.load(f)

model.fit(data)
pre = model.predict(data)
print(set(pre))
print(pre)
print(model.get_params())

with open("tmp/output.txt", "w", encoding="utf-8") as f:
    print("Labels:")
    print(pre)
    print("Weights:")
    print(model.weights_)
    print("Means:")
    print(model.means_)
    print("Covariances:")
    print(model.covariances_)
    f.write("Labels:\n")
    for i, p in enumerate(pre):
        f.write(str(p) + ",")
        if i%50 == 0:
            f.write("\n")
    f.write("\n")
    f.write("Weights:\n")
    f.write(str(model.weights_))
    f.write("\n")
    f.write("Means:\n")
    f.write(str(model.means_))
    f.write("\n")
    f.write("Covariances:\n")
    f.write(str(model.covariances_))
    f.write("\n")

# プロット
ci = 0
for k in set(pre):
    Y = []
    Y.append([])
    Y.append([])
    for i, x in enumerate(data):
        if pre[i] == k:
            Y[0].append(x[0])
            Y[1].append(x[1])
    K = k+3
    col = [((K*20)%255)/255,((K*30)%255)/255,((K*50)%255)/255]
    plt.scatter(Y[0], Y[1], c=col)
    ci += 1
plt.show()

