#-*- coding: utf-8 -*-

import dill
from datetime import datetime

# 可変長ngram を用いて，各タイプごとの部分文字列の出現確率の積でタイプを識別する
# まずは簡単に 1文字まで分解しよう

ALPHA = 1.0e-12
# ALPHA = 0.1

THETA = 0.7

NGRAM_HIGH = 4
NGRAM_LOW  = 2

class TypeModel:
    def __init__(self, typename):
        self.typename = typename
        self.hist = []
        self.hist.append({})
        self.count = 0

    # 総文字数を出力する
    def getNumofChars(self, n=0):
        return sum(self.hist[n].values())

    # 総文字種類数を出力する
    def getKindsofChars(self, n=0):
        return len(self.hist[n])
    # 総名前数を出力する
    def getNumofNames(self):
        return self.count

    # 未知文字の重みを返す
    def alpha(self, n=0):
        output = ALPHA
        for i in range(n):
            output = output * 100
        return output

    # 名前を代入してヒストグラムを更新する
    def inputName(self, name, eliminate=False):
        self.count = self.count + 1
        buff = ""
        for s in name:
            # バイグラムもついでに保存してみよう
            # バイグラムええやん．トライグラムもやってみようか
            # というか指定した深さまで試せるようにしよう
            buff = buff + s
            for l in range(NGRAM_LOW, NGRAM_HIGH + 1):
                if len(self.hist) < l:
                    self.hist.append({})
                if len(buff) > l:
                    buffL = buff[-1*l:]
                    if eliminate == True:
                        self.hist[l-1][buffL] = self.hist[l-1][buffL] - 1
                        if self.hist[l-1][buffL] == 0:
                            del self.hist[l-1][buffL]
                    elif buffL in self.hist[l-1].keys():
                        self.hist[l-1][buffL] = self.hist[l-1][buffL] + 1
                    else:
                        self.hist[l-1][buffL] = 1
            if eliminate == True:
                self.hist[0][s] = self.hist[0][s] - 1
                if self.hist[0][s] == 0:
                    del self.hist[0][s]
            elif s in self.hist[0].keys():
                self.hist[0][s] = self.hist[0][s] + 1
            else:
                self.hist[0][s] = 1
        # print(name + "  \t->\t" + encoded)

    # 配列で代入すると全部の名前代入する君
    def inputNameList(self, namelist):
        for n in namelist:
            self.inputName(n)

    # 事後確率計算
    def calcProbability(self, name):
        output = 1
        buff = ""
        for s in name:
            buff = buff + s
            if s in self.hist[0].keys():
                output = output * ((self.hist[0][s])/(self.getNumofChars()+self.alpha()))
            else:
                output = output * (self.alpha()/(self.getNumofChars()+self.alpha()))
            for l in range(NGRAM_LOW, NGRAM_HIGH + 1):
                if len(buff) > l:
                    buffL = buff[-1*l:]
                    if len(self.hist) >= l and buffL in self.hist[l-1].keys():
                        output = output * ((self.hist[l-1][buffL])/(self.getNumofChars(l-1)+self.alpha(l-1)))
                    else:
                        output = output * (self.alpha(l-1)/(self.getNumofChars(l-1)+self.alpha(l-1)))
                    
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

    # 指定したタイプから指定したポケモンの情報を削除する
    def eliminateName(self, name, types, eliminate=True):
        for t in types:
            if t == "":
                continue
            self.models[t].inputName(name, eliminate)

    # 名前を引数にタイプを推定する
    # 引数 theta は閾値．これを下回るとタイプ2は なし になる
    # 閾値は値よりもタイプ1に対する割合とかの方がよさそう
    def predict(self, name, theta=THETA, out=None):
    # def predict(self, name, theta=1.0e-06, out=None):
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
        if (scores[1]/scores[0]) < theta:
        # if scores[0] < theta:
            types[1] = ""
            scores[1] = theta
        print("Predicted type of "+name)
        print("("+types[0]+":"+str(scores[0])+")")
        print("("+types[1]+":"+str(scores[1])+")")
        if out != None:
            out.write("Predicted type of "+name+"\n")
            out.write("("+types[0]+":"+str(scores[0])+")\n")
            out.write("("+types[1]+":"+str(scores[1])+")\n")
        return {"types":types, "scores":scores}

if __name__ == "__main__":
    datas = {}
    with open("pokemon_alopez247.csv", "r", encoding="utf-8") as f:
        # 1行目はデータの説明なのでスキップ
        line = f.readline().split(",")
        while True:
            line = f.readline().split(",")
            if len(line) < 2:
                break
            if line[2] not in datas.keys():
                datas[line[2]] = []
            datas[line[2]].append(line[1])
            if line[3] != "":
                if line[3] not in datas.keys():
                    datas[line[3]] = []
                datas[line[3]].append(line[1])
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
    with open("type_names_dict.dill", "rb") as f:
        datas = dill.load(f)
    # 各タイプのモデルを生成してみよう
    phist = PHist()
    phist.fit(datas)
    # どの程度正解するか見てみよう
    with open("result/result" + str(int(datetime.now().timestamp())) + ".txt", "w", encoding="utf-8") as res:
        with open("pokemon_alopez247.csv", "r", encoding="utf-8") as f:
            line = f.readline().split(",")
            count = 0
            success_fir = 0
            success_sec = 0
            success_nop = 0
            success_rev = 0
            count_twoType = 0
            count_true_twoType = 0
            while len(line) > 2:
                predicted = phist.predict(line[1], out=res)["types"]
                expected  = [line[2], line[3]]
                count = count + 2
                if predicted[0] == expected[0]:
                    success_fir = success_fir + 1
                if predicted[1] == expected[1]:
                    if predicted[1] == "":
                        success_nop = success_nop + 1
                    else:
                        success_sec = success_sec + 1
                # 順番は間違えているけどタイプを正解している個数
                # 確認のために, どのポケモンのどのタイプだったか出力してみる
                if predicted[0] == expected[1]:
                    # print("rev sample:")
                    # print(line[0] + " : " + str(predicted[0]) + "predicted:0, expected:1")
                    success_rev = success_rev + 1
                if predicted[1] == expected[0]:
                    # print("rev sample:")
                    # print(line[0] + " : " + str(predicted[1]) + "predicted:1, expected:0")
                    success_rev = success_rev + 1
                if predicted[1] != "":
                    count_twoType = count_twoType + 1
                if expected[1] != "":
                    count_true_twoType = count_true_twoType + 1
                line = f.readline().split(",")
        print("result:")
        print(str(success_fir + success_sec + success_nop + success_rev) + "/" + str(count))
        print("fir:" + str(success_fir) + "  sec:" + str(success_sec) + "  nop:" + str(success_nop))
        print("rev:" + str(success_rev))
        print("has two types:" + str(count_twoType) + "/" + str(count_true_twoType))
        res.write("result:\n")
        res.write(str(success_fir + success_sec + success_rev + success_nop) + "/" + str(count) + "\n")
        res.write("fir:" + str(success_fir) + "  sec:" + str(success_sec) + "  nop:" + str(success_nop) + "\n")
        res.write("rev:" + str(success_rev) + "\n")
        res.write("has two types:" + str(count_twoType) + "/" + str(count_true_twoType) + "\n")
    # クロスバリデーションで検定してみよう
    with open("result/resultCV" + str(int(datetime.now().timestamp())) + ".txt", "w", encoding="utf-8") as res:
        with open("pokemon_alopez247.csv", "r", encoding="utf-8") as f:
            line = f.readline().split(",")
            line = f.readline().split(",")
            count = 0
            success_fir = 0
            success_sec = 0
            success_nop = 0
            success_rev = 0
            count_twoType = 0
            count_true_twoType = 0
            while len(line) > 2:
                expected  = [line[2], line[3]]
                phist.eliminateName(line[1], expected)
                predicted = phist.predict(line[1], out=res)["types"]
                phist.eliminateName(line[1], expected, eliminate=False)
                count = count + 2
                if predicted[0] == expected[0]:
                    success_fir = success_fir + 1
                if predicted[1] == expected[1]:
                    if predicted[1] == "":
                        success_nop = success_nop + 1
                    else:
                        success_sec = success_sec + 1
                # 順番は間違えているけどタイプを正解している個数
                # 確認のために, どのポケモンのどのタイプだったか出力してみる
                if predicted[0] == expected[1]:
                    # print("rev sample:")
                    # print(line[0] + " : " + str(predicted[0]) + "predicted:0, expected:1")
                    success_rev = success_rev + 1
                if predicted[1] == expected[0]:
                    # print("rev sample:")
                    # print(line[0] + " : " + str(predicted[1]) + "predicted:1, expected:0")
                    success_rev = success_rev + 1
                if predicted[1] != "":
                    count_twoType = count_twoType + 1
                if expected[1] != "":
                    count_true_twoType = count_true_twoType + 1
                line = f.readline().split(",")
        print("result:")
        print(str(success_fir + success_sec + success_nop + success_rev) + "/" + str(count))
        print("fir:" + str(success_fir) + "  sec:" + str(success_sec) + "  nop:" + str(success_nop))
        print("rev:" + str(success_rev))
        print("has two types:" + str(count_twoType) + "/" + str(count_true_twoType))
        res.write("result:\n")
        res.write(str(success_fir + success_sec + success_rev + success_nop) + "/" + str(count) + "\n")
        res.write("fir:" + str(success_fir) + "  sec:" + str(success_sec) + "  nop:" + str(success_nop) + "\n")
        res.write("rev:" + str(success_rev) + "\n")
        res.write("has two types:" + str(count_twoType) + "/" + str(count_true_twoType) + "\n")
