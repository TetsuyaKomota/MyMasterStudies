# coding = utf-8
import numpy as np

import chainer
import chainer.functions as F
from chainer import initializers
import chainer.links as L
import cv2
import glob
import os
import dill
from sklearn.cross_validation import train_test_split
from sklearn.datasets import fetch_mldata



class Alex(chainer.Chain):

    """Single-GPU AlexNet without partition toward the channel axis."""

    insize = 227

    def __init__(self):
        super(Alex, self).__init__()
        with self.init_scope():
            """
            self.conv1 = L.Convolution2D(None,  96, 11, stride=4)
            self.conv2 = L.Convolution2D(None, 256,  5, pad=2)
            self.conv3 = L.Convolution2D(None, 384,  3, pad=1)
            self.conv4 = L.Convolution2D(None, 384,  3, pad=1)
            self.conv5 = L.Convolution2D(None, 256,  3, pad=1)
            self.fc6 = L.Linear(None, 4096)
            self.fc7 = L.Linear(None, 4096)
            self.fc8 = L.Linear(None, 4)
            """
            self.conv1 = L.Convolution2D(None, 20,  5)
            self.conv2 = L.Convolution2D(None, 50,  5)
            self.fc3 = L.Linear(None, 500)
            self.fc4 = L.Linear(None,  10)

    def __call__(self, x, t):
        """
        h = F.max_pooling_2d(F.local_response_normalization(
            F.relu(self.conv1(x))), 3, stride=2)
        h = F.max_pooling_2d(F.local_response_normalization(
            F.relu(self.conv2(h))), 3, stride=2)
        h = F.relu(self.conv3(h))
        h = F.relu(self.conv4(h))
        h = F.max_pooling_2d(F.relu(self.conv5(h)), 3, stride=2)
        h = F.dropout(F.relu(self.fc6(h)))
        h = F.dropout(F.relu(self.fc7(h)))
        h = self.fc8(h)
        """
        h = F.relu(self.conv1(x))
        h = F.relu(self.conv2(h))
        h = F.relu(self.fc3(h))
        h = self.fc4(h)

        loss = F.softmax_cross_entropy(h, t)
        chainer.report({'loss': loss, 'accuracy': F.accuracy(h, t)}, self)
        return loss

if __name__ == "__main__":
    """
    # データセットを読み込む
    print("load img dataset")
    X = []
    y = []
    imgpaths = glob.glob("tmp/face/resized/*")
    for i, chara in enumerate(["aya", "azusa", "kurumi", "rize"]):
        for imgpath in imgpaths:
            if chara not in os.path.basename(imgpath):
                continue
            img = cv2.imread(imgpath)
            img = img.transpose((1, 2, 0))
            X.append(img)
            y.append(i)

    X = np.array(X, dtype=np.float32)
    y = np.array(y, dtype=np.int32)
    
    # ピクセルの値を0.0-1.0に正規化
    X /= X.max()

    """
    # MNISTデータをロード
    print("load MNIST dataset")
    mnist = fetch_mldata('MNIST original', data_home=".")
    X = mnist.data
    y = mnist.target
    X = X.astype(np.float32)
    y = y.astype(np.int32)

    # ピクセルの値を0.0-1.0に正規化
    X /= X.max()

    # 訓練データとテストデータに分割
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1)

    N = y_train.size
    N_test = y_test.size

    # 画像を (nsample, channel, height, width) の4次元テンソルに変換
    # MNISTはチャンネル数が1なのでreshapeだけでOK
    X_train = X_train.reshape((len(X_train), 1, 28, 28))
    X_test = X_test.reshape((len(X_test), 1, 28, 28))

    # モデルを召喚
    model = Alex()
    model(X_train, y_train)
