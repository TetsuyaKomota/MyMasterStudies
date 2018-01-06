# coding = utf-8

# SOINN のコードがあまりに雑だったので書き直した

import numpy as np
from functools import reduce
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
import dill

# findWinners の出力に対して使うエイリアス
IDX      = 0
DISTANCE = 1

class SOINN:

    # edgeDict は (idxStart, idxGoal) をキーに，Age を値にする
    # idxStart < idxGoal
    def __init__(self, D, N, E):
        self.nodeList   = []
        self.edgeDict   = {}
        self.dimension  = D
        self.nodeAge    = N
        self.edgeAge    = E
        self.inputCount = 0

    # データを代入し，学習する
    def fit(self, X, n_iter=1, prunning=False, verbose=0):
        for epoch in range(max(1, n_iter)):
            temp = 0
            for x in X:
                # np.array に直す(元々 np.array なら何も変わらない)
                xn = np.array(x)

                # dimension 次元のベクトルでないならエラー
                if len(xn.shape) != 1 or xn.shape[0] != self.dimension:
                    print("[SOINN]fit:invalid input:" + str(x))
                    return 

                # データを入力
                self.inputSignal(xn)

                if verbose > 0 and self.inputCount % 100 == 0:
                    temp += 100
                    text  = "[SOINN]fit:"
                    text += "epoch:(%d/%d)  "
                    text += "datas:(%d/%d)  "
                    print(text % (epoch+1, max(1, n_iter), temp, len(X)))

                # 入力回数が nodeAge になったとき．孤立ノードを除去
                if self.inputCount % self.nodeAge == 0:
                    print("あらよっと")
                    self.removeUnnecessaryNode()
                    self.classifier()
            
            self.classifier()
            if prunning == True:
                self.prunning()


    # データを代入し，推定する
    def predict(self, Z, preprocess=False):
        # 一旦孤立ノードを除去し，ラベルを貼る
        if preprocess == True:
            self.removeUnnecessaryNode()
            self.classifier()

        output = []

        for z in Z:
            # np.array に直す(元々 np.array なら何も変わらない)
            zn = np.array(z)
            # dimension 次元のベクトルでないならエラー
            if len(zn.shape) != 1 or zn.shape[0] != self.dimension:
                print("[SOINN]fit:invalid input:" + str(z))
                return 

            # 勝者ノードのラベルを取得
            winners = self.findWinners(zn)
            output.append(self.nodeList[winners[IDX][0]].classID)
          
        return output 

    def inputSignal(self, signal):
        self.inputCount += 1
        if len(self.nodeList) < 2:
            self.nodeList.append(Node(signal))
            return

        # 勝者ノード取得
        winners = self.findWinners(signal)

        # 第1勝者の勝者回数をインクリメント
        self.nodeList[winners[IDX][0]].winCount += 1

        # 勝者ノードの閾値を取得
        threshold = []
        threshold.append(self.calcThreshold(winners[IDX][0])) # 第1勝者
        threshold.append(self.calcThreshold(winners[IDX][1])) # 第2勝者

        # 入力が各閾値内であるか
        flag = []
        flag.append(winners[DISTANCE][0] <= threshold[0])
        flag.append(winners[DISTANCE][1] <= threshold[1])

        # どちらかの閾値の外の場合，新たにノードを追加する
        if flag[0] == False or flag[1] == False:
            self.nodeList.append(Node(signal))
            return
        # 両方の閾値内の場合，勝者ノード間にエッジを生成する
        else:
            # 第1勝者ノードに接続するエッジの年齢をインクリメント
            self.enoldEdge(winners[IDX][0])
          
            # 第2勝者との間のエッジの年齢を 0 に初期化 
            self.edgeDict[(winners[IDX][0], winners[IDX][1])] = 0
           
            # 第1勝者とその隣接ノードを更新 
            self.updateNode(signal, winners[IDX][0])

    # 指定したノードに接続する全エッジの年齢をインクリメント
    def enoldEdge(self, idxNode):
        keyList = [key for key in self.edgeDict.keys() if idxNode in key]
        for key in keyList:
            self.edgeDict[key] += 1
            # edgeAge を超えたエッジは削除
            if self.edgeDict[key] > self.edgeAge:
                print("は～いよっと")
                del self.edgeDict[key]

    # 指定したノードとその隣接ノードを更新
    def updateNode(self, signal, idxFst):
        # 第1勝者に signal を累積平均で足す
        winCount = self.nodeList[idxFst].winCount
        self.nodeList[idxFst].signal  += signal/(winCount + 1)

        # 隣接ノードに微小量を足す
        neighbors = self.findNeighbors(idxFst)
        for idx in neighbors:
            self.nodeList[idx].signal += signal/(100*winCount + 1)

    # 全ノードとの距離リストを取得
    def getDistanceList(self, signal):
        return [n.distance(signal) for n in self.nodeList]

    # 勝者ノードの距離とインデックスを取得
    def findWinners(self, signal):
        # 距離計算
        distList = self.getDistanceList(signal)

        # 最小値を取得
        distFst = min(distList)
        idxFst  = distList.index(distFst)

        # 第1勝者部分の距離を最大にしてもう一度最小値を取得
        distList[idxFst] = max(distList)
        distSnd = min(distList)
        idxSnd  = distList.index(distSnd)

        return [[idxFst, idxSnd], [distFst, distSnd]]

    # 指定ノードの隣接ノードのインデックスリストを取得
    def findNeighbors(self, idxNode):
        idxs  = []
        idxs += [key[0] for key in self.edgeDict.keys() if key[1]==idxNode]
        idxs += [key[1] for key in self.edgeDict.keys() if key[0]==idxNode]
        return idxs

    # 指定ノードの閾値を取得
    def calcThreshold(self, idxNode):
        distList = self.getDistanceList(self.nodeList[idxNode].signal)
        neighborList = self.findNeighbors(idxNode)

        # 隣接ノードがないなら最近ノードまでの距離を返す
        if len(neighborList) == 0:
            return min([d for d in distList if d != 0])
        # 隣接ノードがあるならその中の最遠ノードまでの距離を返す
        else:
            return max([distList[i] for i in neighborList])

    # 孤立ノードを除去し，それに対応してエッジのキーを更新
    def removeUnnecessaryNode(self):
        # 孤立ノードのインデックスはエッジのキーに存在しないインデックス
        # 読みにくいけど，エッジのキーを list にキャストして畳み込んでる
        if len(self.edgeDict.keys()) == 0:
            safe = []
        else:
            safe = reduce(lambda x,y:list(x)+list(y), self.edgeDict.keys())
        safe = set(safe)

        # 孤立ノードは safe の補集合
        # np.count_nonzero するために np.array にしている
        idxNodeRange = range(len(self.nodeList))
        isolated     = np.array(list(set(idxNodeRange) - safe))

        # インデックスの補正リストを生成
        # 手前の孤立ノードの数だけインデックスを減らせばいい
        offset = [np.count_nonzero(isolated<i) for i in idxNodeRange]

        # キーを更新
        newEdgeDict = {}
        for key in self.edgeDict:
            idx0 = key[0] - offset[key[0]]
            idx1 = key[1] - offset[key[1]]
            newEdgeDict[(idx0, idx1)] = self.edgeDict[key]
        self.edgeDict = newEdgeDict

        # ノードを更新
        newNodeList = []
        for idx in range(len(self.nodeList)):
            if idx not in isolated:
                newNodeList.append(self.nodeList[idx])
        self.nodeList = newNodeList

    # クラスラベルを貼る
    def classifier(self):
        for node in self.nodeList:
            node.classID = -1
        label = 0
        for idxNode in range(len(self.nodeList)):
            if self.nodeList[idxNode].classID == -1:
                cluster = self.classifier_sub(label, idxNode)
                for c in cluster:
                    self.nodeList[c].classID = label
                label += 1
        return label

    def classifier_sub(self, label, idxNode):
        bList = [idxNode]
        aList = []
        while len(bList) > 0:
            idx = bList.pop(0)
            aList.append(idx)
            bList += self.findNeighbors(idx)
            bList = list(set(bList) - set(aList))
        return aList

    # 微小クラスを削除する
    def prunning(self, minSize=4):
        labelList = [node.classID for node in self.nodeList]
        labelSet  = set(labelList)
        labelDict = {}

        for label in labelSet:
            labelDict[label] = len([0 for l in labelList if l==label])

        removeList = [l for l in labelDict.keys() if labelDict[l]<minSize]

        removeNode = []
        for idx in range(len(self.nodeList)):
            if self.nodeList[idx].classID in removeList:
                removeNode.append(idx)

        removeEdge = []
        for key in self.edgeDict.keys():
            if len(set(key) & set(removeNode)) == 2:
                removeEdge.append(key)

        for key in removeEdge:
            del self.edgeDict[key]

        self.removeUnnecessaryNode()

    # モデルをセーブする
    def saveModel(self, path="tmp/"):
        output = {"node":[], "edge":self.edgeDict}
        for node in self.nodeList:
            nodeInfo = [node.signal, node.age, node.winCount, node.classID]
            output["node"].append(nodeInfo)
        with open(path + str("soinn.dill"), "wb") as f:
            dill.dump(output, f)
        return output

    # モデルをロードする
    def loadModel(self, path="tmp/"):
        with open(path + str("soinn.dill"), "rb") as f:
            model = dill.load(f)
        self.edgeDict = model["edge"]
        self.nodeList = []
        for nodeInfo in model["node"]:
            self.nodeList.append(Node(nodeInfo[0]))
            self.nodeList[-1].age      = nodeInfo[1]
            self.nodeList[-1].winCount = nodeInfo[2]
            self.nodeList[-1].classID  = nodeInfo[3]
        return model

    # ノードを表示する
    def show(self, preprocess=False):
        if preprocess == True:
            self.removeUnnecessaryNode()
            self.classifier()
        X = [node.signal  for node in self.nodeList]
        y = [node.classID for node in self.nodeList]
        
        # 主成分分析して 2次元にする
        pca = PCA(n_components=2)
        Xd = pca.fit_transform(X)

        Xd = np.array(Xd).T

        for l in set(y):
            Xg = [[], []]
            for i in range(len(y)):
                if y[i] == l:
                    Xg[0].append(Xd[0][i])
                    Xg[1].append(Xd[1][i])
            color = (((l*20)%255)/255, ((l*30)%255)/255, ((l*50)%255)/255)
            print(len(Xg[0]))
            print(color)
            plt.scatter(Xg[0], Xg[1], c=color)
        plt.show()

class Node:

    def __init__(self, signal):
        self.signal   = signal
        self.age      = 0
        self.winCount = 0
        self.classID  = -1  
 
    # ユークリッド距離 
    def distance(self, signal):
        return np.linalg.norm(self.signal - signal)


if __name__ == "__main__":

    x = []
    y = []
    for _ in range(1000):
        x.append(np.random.normal(0, 1))
        y.append(np.random.normal(0, 1))
    for _ in range(1000):
        x.append(np.random.normal(10, 1))
        y.append(np.random.normal(0, 1))
    for _ in range(1000):
        x.append(np.random.normal(0, 1))
        y.append(np.random.normal(10, 1))
    for _ in range(1000):
        x.append(np.random.normal(10, 1))
        y.append(np.random.normal(10, 1))

    X = []
    idx = list(range(len(x)))
    np.random.shuffle(idx)
    for i in idx:
        X.append(np.array([x[i], y[i]]))

    soinn = SOINN(2, 500, 50)
    soinn.fit(X, n_iter=1, verbose=1)
    soinn.prunning()
    soinn.show(preprocess=True)
    X = []
    idx = list(range(len(x)))
    for i in idx:
        X.append(np.array([x[i], y[i]]))

    Z = soinn.predict(X)
    # 1000 データずつ確認する．
    # 最も多いラベルを正解とする
    seikai = []
    for i in range(4):
        Zd = Z[i*1000:(i+1)*1000]
        labels = {}
        for zd in Zd:
            if zd in labels.keys():
                labels[zd] += 1
            else:
                labels[zd]  = 1
        ooi = max(labels.values())
        a = [l for l in labels.keys() if labels[l]==ooi][0]
        seikai.append(len([0 for zd in Zd if zd==a]))

    print(seikai)

    L = 10
    for i in range(len(Z)-L):
        Z[i] = sum([Z[i+j] for j in range(L)])/L
    plt.plot(Z)
    plt.show()

    soinn.saveModel()

    zoinn = SOINN(2, 500, 50)
    zoinn.loadModel()
    zoinn.show()

