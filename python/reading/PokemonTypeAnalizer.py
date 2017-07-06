#-*- coding: utf-8 -*-

import dill

# 可変長ngram を用いて，各タイプごとの部分文字列の出現確率の積でタイプを識別する
# まずは簡単に 1文字まで分解しよう

"""
datas = {}
with open("pokemon.csv", "r") as f:
    # print(type(f.readline()))
    # exit()
    line = f.readline().split(",")
    while len(line)>2:
        if line[2] not in datas.keys():
            datas[line[2]] = []
        datas[line[2]].append(line[0])
        if line[3] != "なし":
            if line[3] not in datas.keys():
                datas[line[3]] = []
            datas[line[3]].append(line[0])
        line = f.readline().split(",")
for d in datas:
    print("TYPE:" + str(d))
    temp = ""
    for i, n in enumerate(datas[d]):
        temp = temp + n + ","
        if i%10 == 0 and i != 0:
            print(temp + "\n")
            temp = ""
    print(temp + "\n")

# タイプごとに名前を分類できたのでとりあえず保存しておく
with open("type_names_dict.dill", "wb") as f:
    dill.dump(datas, f)
"""
ALPHA = 0.1

class TypeModel:
    def __init__(self, typename):
        self.typename = typename
        self.hist = {}
        self.count = 0

    # 総文字数を出力する
    def getNumofChars(self):
        return sum(self.hist.values())

    # 総文字種類数を出力する
    def getKindsofChars(self):
        return len(self.hist)
    # 総名前数を出力する
    def getNumofNames(self):
        return self.count

    # 名前を代入してヒストグラムを更新する
    def inputName(self, name):
        self.count = self.count + 1
        for s in name:
            if s in self.hist.keys():
                self.hist[s] = self.hist[s] + 1
            else:
                self.hist[s] = 1
    # 配列で代入すると全部の名前代入する君
    def inputNameList(self, namelist):
        for n in namelist:
            self.inputName(n)

    # 事後確率計算
    def calcProbability(self, name):
        output = 1
        for s in name:
            if s in self.hist.keys():
                output = output * ((self.hist[s]+ALPHA)/self.getNumofChars())
            else:
                output = output * (ALPHA/self.getNumofChars())
        return output

# 各タイプのモデルを総括する学習モデルクラス
class PHist:
    def __init__(self):
        self.models = {}
        self.count = 0

    # 全名前数を出力する
    def getNumofAllNames(self):
        return self.count

    # datas からモデルを生成
    # 全名前数を保持しておく（事前確率の計算のため）
    def fit(self, datas):
        for t in datas:
            self.count = self.count + len(datas[t])
            self.models[t] = TypeModel(t)
            self.models[t].inputNameList(datas[t])

    # 名前を引数にタイプを推定する
    # 引数 theta は閾値．これを下回るとタイプ2は なし になる
    # 閾値は値よりもタイプ1に対する割合とかの方がよさそう
    def predict(self, name, theta=1.0e-12):
        # ピカチュウの確率を計算させてみよう
        types  = []
        scores = []
        types.append("")
        types.append("")
        scores.append(0)
        scores.append(0)
        for m in self.models:
            # 事後確率
            score = self.models[m].calcProbability(name)
            # 事前確率
            score = score*self.models[m].getNumofNames()/self.getNumofAllNames()
            if score > scores[0]:
                types[1] = types[0]
                scores[1] = scores[0]
                types[0] = m
                scores[0] = score
            elif score > scores[1]:
                types[1] = m
                scores[1] = score
        if scores[1] < theta:
            types[1] = "なし"
            scores[1] = theta
        print("Predicted type of "+name)
        print("("+types[0]+":"+str(scores[0])+")")
        print("("+types[1]+":"+str(scores[1])+")")
        return {"types":types, "scores":scores}

if __name__ == "__main__":
    with open("type_names_dict.dill", "rb") as f:
        datas = dill.load(f)
    print("hello")
    # 各タイプのモデルを生成してみよう
    """
    models = {}
    for t in datas:
        models[t] = TypeModel(t)
        models[t].inputNameList(datas[t])
    """
    phist = PHist()
    phist.fit(datas)
    # ピカチュウの確率を計算させてみよう
    """
    types[0] = ""
    scores[0] = 0
    types[1] = ""
    scores[1] = 0
    for m in models:
        print(m + ":")
        score = models[m].calcProbability("ピカチュウ")
        if score > scores[0]:
            types[1] = types[0]
            scores[1] = scores[0]
            types[0] = m
            scores[0] = score
        elif score > scores[1]:
            types[1] = m
            scores[1] = score
    print("Predicted type:")
    print("("+types[0]+":"+str(scores[0])+")")
    print("("+types[1]+":"+str(scores[1])+")")
    """
    phist.predict("ピカチュウ")
    # どの程度正解するか見てみよう
    with open("pokemon.csv", "r") as f:
        line = f.readline().split(",")
        count = 0
        success_fir = 0
        success_sec = 0
        success_rev = 0
        while len(line) > 2:
            predicted = phist.predict(line[0])["types"]
            expected  = [line[2], line[3]]
            count = count + 2
            if predicted[0] == expected[0]:
                success_fir = success_fir + 1
            if predicted[1] == expected[1]:
                success_sec = success_sec + 1
            if predicted[0] == expected[1]:
                success_rev = success_rev + 1
            if predicted[1] == expected[0]:
                success_rev = success_rev + 1
            line = f.readline().split(",")
    print("result:")
    print(str(success_fir + success_sec) + "/" + str(count))
    print("fir:" + str(success_fir) + "  sec:" + str(success_sec))
    print("rev:" + str(success_rev))
