# coding = utf-8

import random
import numpy as np
import dill
import time
from datetime import datetime
from copy import deepcopy
from functools import reduce

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
    # MIN_W  : 単語の最短長さ
    def __init__(self, D, THETA, PAD, LEN, MIN_W, isBase=False):
        self.D           = D
        self.THETA       = THETA
        self.PAD         = PAD
        self.LEN         = LEN
        self.MIN_W       = MIN_W
        self.isBase      = isBase
        # フィールド
        self.restaurants = {():[[], []]}
        self.clean       = 0
        self.timeScore   = {}
        if isBase == False:
            # 単語HPYLM なら，文字HPYLM を持つ
            self.base    = Franchise(D, THETA, 3, 2, 1, True)

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
        # 単語HPYLM なら,文字HPYLM を更新
        if self.isBase == False:
            for w in [s for s in sentence if s != PADWORD]:
                self.base.addSentence(self.forBase(w))

        part = [PADWORD for _ in range(self.LEN)]
        for word in sentence:
            part = part[1:] + [word]
            # すべてパディングであるような文脈は無視
            if part == [PADWORD for _ in range(self.LEN)]:
                continue
            self.addCustomerofWord(tuple(part[:-1]), part[-1])
 
    # 文を代入して客を削除
    # 新実装は全客に対して代理客を生成するので，
    # LEN の長さに分割してそのまま削除するだけでいい
    # 削除に関しては Pitman-Yor 過程する必要なく，
    # また add されている前提なので文脈生成も必要なし
    def eliminateSentence(self, sentence):
        # 単語HPYLM なら,文字HPYLM を更新
        if self.isBase == False:
            for w in [s for s in sentence if s != PADWORD]:
                self.base.eliminateSentence(self.forBase(w))

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
    # 短すぎる単語を無視する項を追加
    def calcProbabilityofBaseMeasure(self, w):
        if self.isBase == False:
            # 単語HPYLM なら，文字HPYLM から取得してくる
            return self.base.calcProbability(self.forBase(w))
        else:
            # 文字HPYLM なら，各文字の一様分布
            # 根店のテーブルに配置されているのが全文字のはず
            charset = set([t[1] for t in self.getRestaurant(())[TABLE]])
            # PADWORD が含まれているので 1 引く
            return 1.0/(len(charset)-1)

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
    # fit : boolean : モデルの更新をするか
    #                 学習時には True, 分割の推定時には False
    #                 executeParsing の引数で指定する
    def sampling(self, sentence, fit):
        timeScore = []
        # 古い文章を削除
        if fit == True:
            self.eliminateSentence(sentence)
        newSentence = deepcopy(sentence)
        # 終始端単語を無視
        length = sum([len(w) for w in sentence if w!=PADWORD])-1
        idxList = list(range(length))
        random.shuffle(idxList)
        # 始端単語を無視するためのオフセット
        padlen = len(PADWORD)*self.PAD+1
        p_a = 1.0
        p_b = 1.0
        for idx in idxList:
            newSentence_a = self.changeBoundary(newSentence, idx+padlen)
            p_b = self.calcProbability(newSentence)
            p_a = self.calcProbability(newSentence_a)
        if random.random() < p_a / (p_a + p_b):
            newSentence = newSentence_a
        # 新しい文章を挿入
        if fit == True:
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
    # rev : boolean : 逆向きにした文字列の分割を併用して行うか
    #                 True にした場合，reverseSentences した文字列も
    #                 対象に加えて解析を行う
    #
    # fit : boolean : モデルの更新を行うか
    #                 学習時には True, 分割の推定時には False を指定する
    def executeParsing(self, sentenceDict, n_iter, rev=False, fit=True):
        current = deepcopy(sentenceDict)
        if rev == True:
            current = self.reverseSentences(current)
        PADS = [PADWORD for _ in range(self.PAD)]
        for c in current:
            current[c] = deepcopy(PADS)+current[c]+deepcopy(PADS)
            if fit == True:
                self.addSentence(current[c])
        for i in range(n_iter):
            for c in current:
                current[c] = self.sampling(current[c], fit)
            if i % (int(n_iter/10)) == 0:
                print("[RefactedRest]executeParsing:iteration:"+str(i))
                print("[RefactedRest]executeParsing:currentSentences:")
                for c in sorted(list(current.keys())):
                    # print(c + ":" + str(current[c]))
                    print(c + ":" + self.showSentence(current, c))
        for c in current:
            current[c] = [w for w in current[c] if w != PADWORD] 
        if rev == True:
            current = self.reverseSentences(current)
        print("[RefactedRest]executeParsing:results:")
        for c in current:
            print(c + ":" + str(current[c]))
        # 最後に掃除する
        self.cleanEmptyRestaurant()
        return current

    # 学習済みのモデルを使って，文の分割を推定する
    def predict(self, sentences):
        output = {}

        # 単語の集合は根店のテーブル配列を使えばいいはず
        baseTableList = self.restaurants[()][TABLE]
        wordSet = set([t[T_WORD] for t in baseTableList])

        for filename in sentences.keys():
            # 対象に含まれる単語のみのサブセットを取得
            code = sentences[filename][0]
            wordSubSet = set([w for w in wordSet if w in code])

            # 可能な分割を取得
            segList = self.predict_sub(wordSubSet, code)

            # PAD つける
            p       = [PADWORD for _ in range(self.PAD)]
            segList = [p+s+p for s in segList]

            # 各分割の確率を求める
            probList = [self.calcProbability(s) for s in segList]

            # 最も高確率である分割を取得
            idx = probList.index(max(probList))
            output[filename] = segList[idx]

            # PAD 外す
            output[filename] = output[filename][self.PAD:-1*(self.PAD+1)]

        return output

    # 可能な単語分割を取得する再帰関数
    def predict_sub(self, wordSet, code):
        # wordSet が空なら，code は未知語
        if len(wordSet) == 0:
            return [[code]]
        # 単語が一つも含まれていないなら code は未知語
        check = reduce(lambda x,y:x or y, [w in code for w in wordSet])
        if check == False:
            return [[code]]
        
        # 左端に単語があるなら，その単語を分割して再帰
        # 最終的に配列の配列が返ってくるはずなので，分割した単語を
        # 左端に append して return 
        check = [w for w in wordSet if code[:len(w)]==w]
        if len(check) > 0:
            output = []
            for w in check:
                temp = self.predict_sub(wordSet, code[len(w):])
                output += [[w]+r for r in temp]
            return output 

        # 左端に単語がないなら，単語が現れるまでを未知語として分割
        else:
            unknown = ""
            nextcode = code
            while True:
                check = [w for w in wordSet if nextcode[:len(w)]==w]
                if len(check) > 0:
                    break
                unknown += nextcode[0]
                nextcode = nextcode[1:]
            temp = self.predict_sub(wordSet, nextcode)
            output = [[unknown]+r for r in temp]           
            return output

    def debug_start(self, idx):
        if idx not in self.timeScore.keys():
            self.timeScore[idx] = []
        self.timeScore[idx].append(datetime.now().timestamp())

    def debug_endof(self, idx):
        if idx not in self.timeScore.keys():
            return 
        self.timeScore[idx][-1] *= -1
        self.timeScore[idx][-1] += datetime.now().timestamp()

    def debug_result(self):
        output = {}
        for idx in self.timeScore.keys():
            scores = self.timeScore[idx]
            output[idx] = sum(scores)/len(scores)
        return output

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

    # executeParsing の際に分割結果を表示する関数
    # そのまま出力すると制御文字とか使う場合あるので変換して出す
    def showSentence(self, sList, sName):
        s = sList[sName]
        text = "["
        for w in s:
            encW = "'"
            for c in w:
                if c == PADWORD:
                    encW += c
                else:
                    ordC = self.retranslate(c)
                    encC = self.translate(ordC%52)
                    idxC = int(ordC/52)
                    encW += encC
                    if idxC > 0:
                        encW += str(idxC)
            encW += "'"
            text += encW + ","
        text = text[:-1] + "]"
        return text

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

    # 単語を引数に，文字HPYLM に渡すためのリストに変換する
    def forBase(self, word):
        output = list(word)
        pads   = [PADWORD for _ in range(self.base.PAD)]
        return pads + output + pads

if __name__ == "__main__":
    f = Franchise(1, 200, 3, 3, 2)

    data = {}
    """
    data["1"] = ["りんごぶどうみかんばななもも"]
    data["2"] = ["ももみかんばななりんごぶどう"]
    data["3"] = ["ぶどうばななみかんりんごもも"]
    data["4"] = ["ばななりんごみかんももぶどう"]
    data["5"] = ["みかんももばななりんごぶどう"]
    """
    for i in range(5):
        idx = "{0:02d}".format(i)
        data[idx] = [""]
        for _ in range(3):
            # r = random.random()
            r = random.random()/2
            if r < 0.1:
                data[idx][0] += "apple"
            elif r < 0.2:
                data[idx][0] += "grape"
            elif r < 0.3:
                data[idx][0] += "banana"
            elif r < 0.4:
                data[idx][0] += "peach"
            # elif r < 0.5:
            else:
                data[idx][0] += "orange"
            """
            elif r < 0.6:
                data[idx][0] += "melon"
            elif r < 0.7:
                data[idx][0] += "strawberry"
            elif r < 0.8:
                data[idx][0] += "lychee"
            elif r < 0.9:
                data[idx][0] += "watermelon"
            else:
                data[idx][0] += "pineapple"
            """

    for i in sorted(list(data.keys())):
        print(i + ":" + str(data[i]))
        print(i + ":" + f.showSentence(data, i))

    # print(f.reverseSentences(data))

    for i in range(1):
        with open("tmp/RefactedRest_result.dill", "wb") as g:
            ptime = datetime.now().timestamp()
            dill.dump(f.executeParsing(data, 300), g)
            ptime = datetime.now().timestamp() - ptime

    f.toPrint()
    res = f.debug_result()
    for r in res:
        print(r + "\t\t: " + str(res[r]))
