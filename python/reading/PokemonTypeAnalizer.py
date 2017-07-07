#-*- coding: utf-8 -*-

import dill

# 可変長ngram を用いて，各タイプごとの部分文字列の出現確率の積でタイプを識別する
# まずは簡単に 1文字まで分解しよう

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

    # 入力文字をア行に変換する
    # ャュョはャに統一
    # ワヲンはそのまま使う
    def encodeChar(self, char):
        if char in {"ワ", "ヲ", "ン", "ー", "ッ", "♂", "♀"}:
            return char
        elif char in {"ァ", "ィ", "ゥ", "ェ", "ォ"}:
            return "ァ"
        elif char in {"ヤ", "ユ", "ヨ"}:
            return "ヤ"
        elif char in {"ャ", "ュ", "ョ"}:
            return "ャ"
        elif char in {"ア", "イ", "ウ", "エ", "オ"}:
            return "ア"
        elif char in {"カ", "キ", "ク", "ケ", "コ"}:
            return "カ"
        elif char in {"サ", "シ", "ス", "セ", "ソ"}:
            return "サ"
        elif char in {"タ", "チ", "ツ", "テ", "ト"}:
            return "タ"
        elif char in {"ナ", "ニ", "ヌ", "ネ", "ノ"}:
            return "ナ"
        elif char in {"ハ", "ヒ", "フ", "ヘ", "ホ"}:
            return "ハ"
        elif char in {"マ", "ミ", "ム", "メ", "モ"}:
            return "マ"
        elif char in {"ラ", "リ", "ル", "レ", "ロ"}:
            return "ラ"
        elif char in {"ガ", "ギ", "グ", "ゲ", "ゴ"}:
            return "ガ"
        elif char in {"ザ", "ジ", "ズ", "ゼ", "ゾ"}:
            return "ザ"
        elif char in {"ダ", "ヂ", "ヅ", "デ", "ド"}:
            return "ダ"
        elif char in {"バ", "ビ", "ブ", "ベ", "ボ"}:
            return "バ"
        elif char in {"パ", "ピ", "プ", "ペ", "ポ"}:
            return "パ"
        else:
            return "NC"

    # 名前を代入してヒストグラムを更新する
    def inputName(self, name):
        self.count = self.count + 1
        encoded = ""
        for S in name:
            # s = self.encodeChar(S)
            s = S
            encoded = encoded + s
            # s = S
            if s != "NC" and s in self.hist.keys():
                self.hist[s] = self.hist[s] + 1
            else:
                self.hist[s] = 1
        print(name + "->" + encoded)

    # 配列で代入すると全部の名前代入する君
    def inputNameList(self, namelist):
        for n in namelist:
            self.inputName(n)

    # 事後確率計算
    def calcProbability(self, name):
        output = 1
        for S in name:
            # s = self.encodeChar(S)
            s = S
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
    def predict(self, name, theta=1.0e-06):
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
    datas = {}
    with open("pokemon.csv", "r", encoding="utf-8") as f:
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
    """
    # タイプごとに名前を分類できたのでとりあえず保存しておく
    with open("type_names_dict.dill", "wb") as f:
        dill.dump(datas, f)
    with open("type_names_dict.dill", "rb") as f:
        datas = dill.load(f)
    """
    print("hello")
    # 各タイプのモデルを生成してみよう
    phist = PHist()
    phist.fit(datas)
    # どの程度正解するか見てみよう
    with open("pokemon.csv", "r", encoding="utf-8") as f:
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
    # 実在しないポケモンのタイプを予想しよう
    phist.predict("ヒノアラシ")
    phist.predict("ワニノコ")
    phist.predict("チコリータ")
