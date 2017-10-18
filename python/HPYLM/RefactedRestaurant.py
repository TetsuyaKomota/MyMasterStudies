# coding = utf-8

import random
import numpy as np
import dill
import time
from copy import deepcopy

# restaurants は各要素 [[テーブル配列], [客配列]]
# それを識別するための定数
TABLE    = 0
CUSTOMER = 1

# テーブル配列の要素は [親文脈のテーブルid, 単語]とする
# eliminate する際に親文脈から削除するときに必要であるため
# それを識別するための定数
T_PID   = 0
T_WORD  = 1

# 根文脈のテーブルにつける PID
BASE_PID = -1

# 終始端単語
PADWORD = "~"

# Pitman-Yor 過程における新要素
NEW = "THIS CHOICE MEANS NEW FACTOR PICKED PARENT MEASURE"

class Franchise:
   
    # A      : 基底測度のパラメータ 
    # D      : 割引率
    # THETA  : 強度
    # PAD    : 終始端単語の数
    # LEN    : 文脈長さ
    def __init__(self, D, A, THETA, PAD, LEN):
        self.D           = D
        self.A           = A
        self.THETA       = THETA
        self.PAD         = PAD
        self.LEN         = LEN
        self.restaurants = {():[[], []]}
        self.clean       = 0

    def getTheta(self, u):
        return self.THETA * (len(u) + 1.0)

    def getD(self, u):
        return (self.D*len(u)) / (len(u)+1.0)

    # テーブル ID 指定でそのテーブルの客のID配列を取得
    # 客数を知りたいときはこれを len すればいい
    def getCustomerListofTable(self, u, tableId):
        rest = self.getRestaurant(u)
        return [i for i, c in enumerate(rest[CUSTOMER]) if c==tableId]

    def getTableListofWord(self, u, word):
        rest = self.getRestaurant(u)
        return [i for i, t in enumerate(rest[TABLE]) if t[T_WORD]==word]

    def getCustomerListofWord(self, u, word):
        rest = self.getRestaurant(u)
        customerList = []
        tids = self.getTableListofWord(u, word)
        for tid in tids:
            customerList += self.getCustomerListofTable(u, tid)
        return customerList

    def addTableofWord(self, u, pid, word):
        rest = self.getRestaurant(u)
        rest[TABLE].append([pid, word])

    def addCustomerofTable(self, u, tableId):
        rest = self.getRestaurant(u)
        rest[CUSTOMER].append(tableId)
        # そのテーブルを生成した親文脈のテーブルにも代理客を配置
        if len(u) > 0:
            pid = rest[TABLE][tableId][T_PID]
            self.addCustomerofTable(u[1:], pid)

    def eliminateCustomerofTable(self, u, tableId):
        rest = self.getRestaurant(u)
        pid  = rest[TABLE][tableId][T_PID]
        CustomerList = self.getCustomerListofTable(u, tableId)
        if len(CustomerList) == 0:
            print("多分何かがおかしいよ")
            return
        delCustomer = CustomerList[0]
        del rest[CUSTOMER][delCustomer]
        if len(self.getCustomerListofTable(u, tableId)) == 0:
            self.eliminateTable(u, tableId)
        # そのテーブルを生成した親文脈のテーブルから代理客を削除
        if len(u) > 0:
            self.eliminateCustomerofTable(u[1:], pid)

    def eliminateTable(self, u, tableId):
        rest = self.restaurants[u]
        # その文脈の客のテーブルID を修正
        for i, c in enumerate(rest[CUSTOMER]):
            if c > tableId:
                rest[CUSTOMER][i] -= 1
        # 子文脈の PID も修正する
        for cu in [cu for cu in self.restaurants.keys() if cu[1:]==u]:
            for t in self.restaurants[cu][TABLE]:
                if t[T_PID] > tableId:
                    t[T_PID] -= 1
        del rest[TABLE][tableId]

    # 無駄にあるレストランを削除する
    def cleanEmptyRestaurant(self):
        delList = []
        for u in self.restaurants.keys():
            if u != () and self.restaurants[u] == [[], []]:
                delList.append(u)
        for u in delList:
            del self.restaurants[u]
        self.clean = len(self.restaurants)

    # 文脈を取得する．文脈がない場合は生成する
    def getRestaurant(self, u):
        # 店数が一定以上の場合，無駄な店をクリーニング
        if len(self.restaurants) > 2*self.clean:
            self.cleanEmptyRestaurant()
        self.addRestaurant(u)
        return self.restaurants[u]

    def addRestaurant(self, u):
        # 文脈が LEN より長い場合は生成しない
        if len(u) > self.LEN:
            return 
        # 文脈が存在しないなら新たに生成
        if u not in self.restaurants.keys():
            self.restaurants[u] = [[], []]

    # PitmanYor過程から，指定した単語のテーブルID を取得
    # 単語指定の条件付確率を用いる
    # 新テーブルが選択される場合は NEW を返す
    def pickwithPitmanYor(self, u, word):
        rest = self.getRestaurant(u)
        tableList = self.getTableListofWord(u, word)
        tableHist = {NEW:self.getTheta(u)}
        for tid in tableList:
            tableHist[tid] = len(self.getCustomerListofTable(u, tid))
        total = sum(tableHist.values())
        
        # サンプリングを行う
        rand = random.random()
        temp = 0
        for tid in tableHist:
            temp += tableHist[tid]
            if rand <= temp/total:
                return tid

    # ある文脈に対して単語指定で客を追加する
    # この処理は「テーブルを選択する」という Pitman-Yor 過程と
    # 親文脈に向かう再帰処理が必要
    def addCustomerofWord(self, u, word, add=True):
        tid = self.pickwithPitmanYor(u, word)
        # NEW を引いた場合，親文脈から新テーブルを取得する
        if tid == NEW:
            if len(u) == 0:
                pid = BASE_PID
            else:
                # addCustomerofTable が代理客を生成するので，
                # 新テーブル生成時に代理客を配置しないように
                # add=False とする
                self.addRestaurant(u[:-1])
                pid = self.addCustomerofWord(u[1:], word, add=False)
            self.addTableofWord(u, pid, word)
            tid = len(self.restaurants[u][TABLE])-1
        # 再帰の最初のみ，addCustomerofTable を実行する
        if add == True:
            self.addCustomerofTable(u, tid)
        return tid

    # 文を代入して客を配置
    # 新実装は全客に対して代理客を生成するので，
    # LEN の長さに分割してそのまま代入するだけでいい
    def addSentence(self, sentence):
        part = [PADWORD for _ in range(self.LEN)]
        for word in sentence:
            part = part[1:] + [word]
            # すべてパディングであるような文脈は無視
            if part == [PADWORD for _ in range(self.LEN)]:
                continue
            self.addRestaurant(tuple(part[:-1]))
            self.addCustomerofWord(tuple(part[:-1]), part[-1])
 
    # 文を代入して客を削除
    # 新実装は全客に対して代理客を生成するので，
    # LEN の長さに分割してそのまま削除するだけでいい
    # 削除に関しては Pitman-Yor 過程する必要なく，
    # また add されている前提なので文脈生成も必要なし
    def eliminateSentence(self, sentence):
        part = [PADWORD for _ in range(self.LEN)]
        for word in sentence:
            part = part[1:] + [word]
            # すべてパディングであるような文脈は無視
            if part == [PADWORD for _ in range(self.LEN)]:
                continue
            tid = self.getTableListofWord(tuple(part[:-1]), part[-1])[0]
            self.eliminateCustomerofTable(tuple(part[:-1]), tid)

    # 指定した文脈で，指定した単語が生成される確率
    def calcProbabilityforU(self, u, w):
        c_uw = len(self.getCustomerListofWord(u, w))
        c_u  = len(self.restaurants[u][CUSTOMER])
        t_uw = len(self.getTableListofWord(u, w))
        t_u  = len(self.restaurants[u][TABLE])
        D    = self.getD(u)
        T    = self.getTheta(u)
        if len(u) == 0:
            Ppar = self.calcProbabilityofBaseMeasure(w)
        else:
            Ppar = self.calcProbabilityforU(u[1:], w)
        term1 =  (1.0*(c_uw-D*t_uw)) / (T+c_u)
        term2 = ((1.0*(T+D*t_u)) / (T+c_u)) * Ppar
        return term1 + term2

    # 基底測度は単語長さの正規分布
    def calcProbabilityofBaseMeasure(self, w):
        return np.exp(-len(w) * self.A)

    # 指定した文章の生成確率
    # 終始端単語は含まれている前提
    def calcProbability(self, sentence):
        output = 1
        part = [PADWORD for _ in range(self.LEN)]
        for word in sentence:
            part = part[1:] + [word]
            # すべてパディングであるような文脈は無視
            if part == [PADWORD for _ in range(self.LEN)]:
                continue
            output *= self.calcProbabilityforU(tuple(part[:-1]), part[-1])
        return output 

    # 文章と番号を引数に，境界状態を入れ替える
    def changeBoundary(self, sentence, charsIdx):
        if charsIdx <= 0 or charsIdx >= sum([len(w) for w in sentence]):
            return sentence
        currentNumofChars = 0
        changedIdx  = -1
        while currentNumofChars < charsIdx:
            changedIdx  += 1
            currentNumofChars += len(sentence[changedIdx])

        o =  sentence[:changedIdx]
        if currentNumofChars == charsIdx:
            o += [sentence[changedIdx]+sentence[changedIdx+1]]
            o += sentence[changedIdx+2:]
        else:
            div = charsIdx - (currentNumofChars-len(sentence[changedIdx]))
            o  += [sentence[changedIdx][:div],sentence[changedIdx][div:]]
            o  += sentence[changedIdx+1:]
        return o 

    # サンプリング
    def sampling(self, sentence):
        # 古い文章を削除
        self.eliminateSentence(sentence)
        newSentence = deepcopy(sentence)
        # 終始端単語を無視
        length = sum([len(w) for w in sentence if w!=PADWORD])-1
        idxList = list(range(length))
        random.shuffle(idxList)
        # 始端単語を無視するためのオフセット
        padlen = len(PADWORD)*self.PAD+1
        for idx in idxList:
            newSentence_a = self.changeBoundary(newSentence, idx+padlen)
            p_b = self.calcProbability(newSentence)
            p_a = self.calcProbability(newSentence_a)
            if random.random() < p_a / (p_a + p_b):
                newSentence = newSentence_a
        # 新しい文章を挿入
        self.addSentence(newSentence)
        return newSentence

    # 辞書内の全文章を反転(各単語を反転し，単語の並び自体も反転)
    def reverseSentences(self, sentenceDict):
        output = {}
        for s in sentenceDict:
            output[s] = []
            for i in range(len(sentenceDict[s])):
                output[s].append(sentenceDict[s][-i-1][::-1]) 
        return output

    # 実行
    def executeParsing(self, sentenceDict, n_iter, reverse=False):
        current = deepcopy(sentenceDict)
        if reverse == True:
            current = self.reverseSentences(current)
        PADS = [PADWORD for _ in range(self.PAD)]
        for c in current:
            current[c] = deepcopy(PADS)+current[c]+deepcopy(PADS)
            self.addSentence(current[c])
        for i in range(n_iter):
            for c in current:
                current[c] = self.sampling(current[c])
            if i % (int(n_iter/100)) == 0:
                print("[RefactedRest]executeParsing:iteration:"+str(i))
                print("[RefactedRest]executeParsing:currentSentences:")
                for c in current:
                    print(c + ":" + str(current[c]))
        for c in current:
            current[c] = [w for w in current[c] if w != PADWORD] 
        if reverse == True:
            current = self.reverseSentences(current)
        print("[RefactedRest]executeParsing:results:")
        for c in current:
            print(c + ":" + str(current[c]))
        # 最後に掃除する
        self.cleanEmptyRestaurant()
        return current

    # デバッグ用の出力メソッド
    def toPrint(self):
        print("===================")
        self.sub_toPrint(())
        print("===================")

    def sub_toPrint(self, u):
        rest = self.getRestaurant(u)
        indent = "".join(["\t" for _ in range(len(u))])
        customers = [rest[TABLE][i][T_WORD] for i in rest[CUSTOMER]]
        print(indent + "U:" + str(u))
        print(indent + "W:" + str(customers))
        childs = [cu for cu in self.restaurants.keys() if cu[1:]==u]
        for cu in childs:
            # () が子文脈になるはずはない
            if len(cu) == 0:
                continue
            self.sub_toPrint(cu)

    def translate(self, number):
        # 61 は 「~」, 62 ~ 95 は特殊文字なので飛ばす
        if number >= 61:
            return (chr(ord("A")+number+35))
        return (chr(ord("A")+number))

    # アルファベットを数字に変換
    def retranslate(self, alphabet):
        # 96 以上なら特殊文字回避のため += 36 されてるはず
        if ord(alphabet) - ord("A") >= 97:
            return ord(alphabet) - ord("A") - 35
        return ord(alphabet) - ord("A")

if __name__ == "__main__":
    f = Franchise(1, 1, 1, 3, 3)
    """
    f.addSentence(["今日", "も", "また", "人", "が", "死んだよ"])
    f.addSentence(["今日", "も", "また", "雨", "が", "降ったよ"])
    f.toPrint()
    f.eliminateSentence(["今日", "も", "また", "雨", "が", "降ったよ"])
    f.toPrint()

    test = ["今日", "も", "また", "雨", "が", "降ったよ"]
    for i in range(1, 11):
        print(f.changeBoundary(test, i))
    """

    data = {}
    data["1"] = ["りんごぶどうみかんばななもも"]
    data["2"] = ["ももみかんばななりんごぶどう"]
    data["3"] = ["ぶどうばななみかんりんごもも"]
    data["4"] = ["ばななりんごみかんももぶどう"]
    data["5"] = ["みかんももばななりんごぶどう"]

    # print(f.reverseSentences(data))

    from datetime import datetime
    for i in range(1):
        with open("tmp/RefactedRest_result.dill", "wb") as g:
            ptime = datetime.now().timestamp()
            dill.dump(f.executeParsing(data, 1000), g)
            ptime = datetime.now().timestamp() - ptime

    f.toPrint()
    print(f.restaurants.keys())
    print(len(f.restaurants))
    print(len([1 for r in f.restaurants.values() if len(r[CUSTOMER])+len(r[TABLE])==0]))
    print(ptime)
