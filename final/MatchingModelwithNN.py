# coding = utf-8

# やること
# 境界列(剪定済み) → 境界列(マッチング済み)

# 手順
# 0. 初期状態を before に入れる
# 1. before から十分離れた次の状態を after に入れる
# 2. 以下を複数回繰り返し，学習モデルを複数得る
#   2-1. before から重複サンプリング
#   2-2. サンプリング結果に対応した after を取得
#   2-3. 取得したデータセットでモデルを学習
#   2-4. 再代入で評価して評価値を得ておく
# 3. before それぞれに以下を行い，predict を取得
#   3-1. モデルで推定し，評価値で重みづけ
#   3-2. 和を predict に挿入
# 4. before を output に追加
# 5. before <- predict
# 6.1. に戻る

from keras.models import Sequential
from keras.layers import Dense, Activation
from keras.layers import BatchNormalization
from keras.optimizers import Adam
import dill
import numpy as np
from functools import reduce
from time import sleep

e          = 30  # 許容誤差

# パーセプトロンを生成
def build(numofInput):
    model = Sequential()
    model.add(Dense(numofInput, input_shape=(numofInput, )))
    # model.add(Activation("relu"))
    # model.add(Dense(numofInput))
    model.add(BatchNormalization())
    model.add(Activation("linear"))
    adam = Adam(lr=0.1)
    model.compile(optimizer="sgd", loss="mean_squared_error")
    return model


def matching(dillpath, n_iter):
    # データのロード
    with open("tmp/dills/"+dillpath+"prunned.dill", "rb") as f:
        prunned = dill.load(f)
    keys = prunned.keys()
    size = 0   # データの次元． 2*オブジェクト数
    goal = 0   # 終了状態のステップ数
    datas = {}
    for filename in keys:
        datas[filename] = []
        goal = prunned[filename][-1]
        with open("tmp/log/"+filename+".csv", "r", encoding="utf-8") as f:
            while True:
                line = f.readline().split(",")
                if len(line) < 2:
                    break
                if size == 0:
                    size = len(line[5:-1])
                datas[filename].append([float(l) for l in line[5:-1]])

    # 共通境界推定
    output = {}
    before = {}
    for filename in keys:
        output[filename] = []
        before[filename] = prunned[filename][0]
    while True:
        after = {}
        for fn in keys:
            # before+e より大きい最小の step 
            # before+e 以降に境界がないなら終了状態にする
            later = [s for s in prunned[fn] if s > before[fn]+e]
            if len(later) > 0:
                after[fn] = later[0]
            else:
                after[fn] = prunned[fn][-1]

        for filename in before.keys():
            print(str(before[filename])+"\t--> "+str(after[filename]))
        sleep(10)
 
        # 終了条件
        flagList = [a == goal for a in after.values()]
        flag = reduce(lambda x, y : x and y, flagList)
        if flag == True:
            break
 
        # サンプリング学習を n_iter 回行う
        modelList = []
        for _ in range(n_iter):
            # サンプリング
            model = build(size)
            sampleList = np.random.choice(list(keys), len(keys))
            X = []
            y = []
            for sample in sampleList:
                X.append(np.array(datas[sample][before[sample]]))
                y.append(np.array(datas[sample][after[sample]]))
           
            X = np.array(X)
            y = np.array(y)

            # 学習
            model.fit(X, y, epochs=10000)

            # 評価
            # 評価はサンプリング前のデータを含めて行う
            X = []
            y = []
            for sample in keys:
                X.append(np.array(datas[sample][before[sample]]))
                y.append(np.array(datas[sample][after[sample]]))
 
            X = np.array(X)
            y = np.array(y)

            w = model.evaluate(X, y)

            # 保存
            modelList.append((model, w))

        # 重みをソフトマックスで付けるために，総和を求めておく
        
        print("modelList")
        tempList = [1.0/m[1] for m in modelList]
        print(tempList)
        sleep(10)
        sumexp = sum(tempList)

        # 次を推定する
        predict = {}
        for filename in keys:
            predict[filename] = []
            for m in modelList:
                beforeData = datas[filename][before[filename]]
                beforeData = np.array([beforeData])
                predict[filename].append(m[0].predict(beforeData))
                predict[filename][-1] *= (1.0/m[1])/sumexp
            predict[filename] = sum(predict[filename])

        # before を output に追加
        # 推定結果に最も近い状態を datas から取得
        selected = {}
        for filename in keys:
            output[filename].append(before[filename])
            # 各ステップの状態との距離を計算する
            p = np.array(predict[filename])
            d = datas[filename]
            distList = [np.linalg.norm(np.array(l)-p) for l in d]
            # 遠いステップにはペナルティをつける
            for i in range(len(distList)):
                distList[i] *= 1#+i*0.0001
            # before ステップ以降のみを対象にする
            distList = distList[before[filename]+e:]
            # after を選ぶ段階で else によって 499 になっている場合
            # [before+e:] に要素が存在しない．その時は
            # そのまま nefore を返す 
            if len(distList) == 0:
                selected[filename] = before[filename]
                continue
            selected[filename]  = distList.index(min(distList))
            # before+e ステップ分抜かしているので足しておく
            selected[filename] += before[filename]+e
 
        # before <- selected
        before = selected

  
    with open("tmp/dills/"+dillpath+"matching.dill", "wb")  as f:
        dill.dump(output, f)

    return output

if __name__ ==  "__main__":
    matching("CHEAT/", 10) 
