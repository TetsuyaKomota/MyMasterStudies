import numpy as np
import matplotlib.pylab as plt
import scipy.io
class DPGMM:
    def __init__(self,alpha=1,mu0=0,rho0=1,a0=1,b0=1,max_iter=30):
        self.alpha = alpha
        self.mu0=mu0
        self.rho0=rho0
        self.a0=a0
        self.b0=b0
        self.max_iter=max_iter

    def _init_z(self):
        z = []
        for i in range(self._N):
            z.append(-1)
        return np.array(z)

    def _init_gamma(self):
        return np.random.gamma(self.a0,self.b0)

    def _init_mu(self):
        return np.random.normal(self.mu0,np.sqrt(1.0/(self.rho0*self.gamma)),size=self._D)

    def _sample_z(self):
        for i in range(self._N):
            old_k = self.z[i]
            if old_k!=-1:
                if self.n[old_k]==1:
                    del self.n[old_k]
                    del self.mu[old_k]
                else:
                    self.n[old_k]-=1
            prob = []
            classes = {}
            _k = 0
            for k in self.n:
                if k==self.new_class:
                    mu = self._init_mu()
                    pi = self.alpha
                    new_mu = mu.copy()
                else:
                    mu = self.mu[k]
                    pi = self.n[k]
                prob.append(self._Gaussian_pdf(self._X[i],mu,self.gamma)*pi)
                classes[_k] = k
                _k += 1
            prob = np.array(prob)
            prob = prob/prob.sum()
            new_k = classes[np.random.multinomial(1,prob,size=1).argmax()]
            self.z[i] = new_k
            self.n[new_k]+=1
            if new_k==self.new_class:
                self.mu[self.new_class] = new_mu
                j = 0
                while True:
                    if not j in self.n:
                        self.n[j] = 0
                        self.new_class=j
                        break
                    j += 1

    def _calc_x_bar(self):
        x_bar = {}
        for i in range(self._N):
            k = self.z[i]
            if not k in x_bar: x_bar[k] = 0
            x_bar[k] += self._X[i]
        for k in x_bar:
            x_bar[k] /= self.n[k]
        return x_bar


    def _sample_mu(self):
        x_bar = self._calc_x_bar()
        for k in self.mu:
            loc = (self.n[k]/(self.n[k]+self.rho0))*x_bar[k] + (self.rho0/(self.n[k]+self.rho0))*self.mu0
            scale = np.sqrt(1.0/(self.gamma*(self.n[k]+self.rho0)))
            self.mu[k] = np.random.normal(loc=loc,scale=scale,size=self._D)

    def _sample_gamma(self):
        a = self.a0 + (self._N*self._D)/2.0
        b = self.b0
        x_bar = self._calc_x_bar()
        for k in self.n:
            if self.n[k]==0: continue
            b += (0.5*self.n[k]*self.rho0/(self.n[k]+self.rho0)) * np.linalg.norm(x_bar[k]-self.mu0)**2
        for i in range(self._N):
            k = self.z[i]
            b += 0.5*np.linalg.norm(x_bar[k]-self._X[i])**2
        self.gamma = np.random.gamma(a,1.0/b)

    def _Gaussian_pdf(self,x,mu,gamma):
        return np.exp(-0.5*gamma*np.linalg.norm(x-mu)**2) # not normalized

    def fit(self,X):
        self._X = X
        self._N = X.shape[0]
        self._D = X.shape[1]
        self.z = self._init_z()
        self.new_class = 0
        self.n = {self.new_class:0}
        self.mu = {}
        self.gamma = self._init_gamma()
        remained_iter = self.max_iter
        while True:
            self._sample_z()
            self._sample_mu()
            self._sample_gamma()
            if remained_iter<=0: break
            remained_iter-=1
        return self

    def predict(self,i):
        return self.z[i]

if __name__ == "__main__":
    # パラメータ
    """
    mu = [[5.0,-5.0], [5.0,5.0], [-5.0,-5.0]]
    var = 1.0
    D = len(mu[0])
    K = len(mu)
    N = 30

    # 真のクラスタ割り当て
    true_z = np.zeros(N, dtype=np.int)
    for i in range(N):
        true_z[i] = i%K

    # データ生成
    X = []
    for i in range(N):
        k = true_z[i]
        x = np.random.normal(loc=mu[k], scale=var, size=D)
        X.append(x)
    X = np.array(X)
    """
    X = scipy.io.loadmat("Inputdata.mat")["Inputsample"]
    # フィッティング
    alpha=1.
    mu0=0.
    rho0=1.
    a0=1.
    b0=1.
    max_iter=2
    model = DPGMM(alpha=alpha,mu0=mu0,rho0=rho0,a0=a0,b0=b0,max_iter=max_iter)
    model.fit(X)

    for w in model.z:
        print(w)

    # プロット
    ci = 0
    for k in model.n:
        if model.n[k]==0: continue
        Y = []
        Y.append([])
        Y.append([])
        for i, x in enumerate(X):
            if model.z[i] == k:
                Y[0].append(x[0])
                Y[1].append(x[1])
        # assign = (model.z==k)
        col = [((k*20)%255)/255,((k*30)%255)/255,((k*50)%255)/255]
        plt.scatter(Y[0], Y[1], c=col)
        ci += 1
    plt.show()
    print(model.mu)
    print(model.gamma)
