#-*- coding:utf-8 -*-

import copy
import random
import numpy as np
import dill

# HPYLM において各ノードにあたる「店」クラス

# ====================================================
# 定数

# θ の |u| に関する比例定数
paramTheta = 1.0
# d の |u| に関する比例定数
paramD     = 1.0
# 基底測度の係数
paramA = 2
# 文脈の深さ限界
TERMINAL = 2

class Restaurant:

    # u         : 文脈（根店からの絶対文脈）．店のインデックスと考えてもよい
    # parent    : 親店のオブジェクト
    # childs    : 子店のオブジェクトの辞書．キーを文脈の最後の単語（相対文脈）とする
    # tables    : テーブルの配列,料理（そのテーブルが提供する料理）を要素とする
    # customers : 客の配列, テーブル番号（その客が座っているテーブルのテーブル配列上のインデックス）を要素とする
    def __init__(self, parent, u):
        self.parent = parent
        self.u = u
        self.tables    = []
        self.customers = []
        self.childs    = {}
        # デバッグ用．自分の文脈を表示する
        # print("generated new Context :"+ str(self.getU()))

    # 親店のゲッター
    def getParent(self):
        return self.parent

    # 文脈のゲッター
    def getU(self):
        return self.u

    # 子店数のゲッター．ほぼテスト用
    def getNumofChilds(self):
        return len(self.childs)

    # 強度θのゲッター
    # PY過程における未知数の強度. ディリクレ過程における α
    def getTheta(self):
        # PY過程における割引率．上とともに本来はlen(u) によって決まる関数だが，
        # とりあえず簡単のために定数化
        # return 0.5
        return paramTheta * (len(self.getU()) + 1.0)

    # 割引係数 d のゲッター
    def getD(self):
        # t_uw (店u で料理w のおいてあるテーブルの数=親店から取得した回数)はとりあえず1固定
        # つまりこれはPY ではなくIKN
        # return 0.5
        return (paramD*len(self.getU())) / (len(self.getU())+1.0)


    # テーブルのID を引数に，そのテーブルに客を一人追加する
        # tableId : int : テーブルのID(配列のインデックス)
    def addCustomeratTable(self, tableId):
        self.customers.append(tableId)

    # 料理を引数に，その料理のおかれたテーブルのいずれかに客を一人追加する
    # 現段階では料理一種につきテーブル一つなので成立する
        # w : str : 料理
    def addCustomeratWord(self, w):
        flag = False
        newId = -1
        for i in range(len(self.tables)):
            if self.tables[i] == w:
                newId = i
                flag = True
                break
        # 指定した料理のテーブルがない場合は新設する
        if flag == False:
            newId = self.addNewTable(w)
            # 新設した場合，親店へ代理客を送る
            if self.parent is not None:
                self.parent.addCustomeratWord(w)
        self.addCustomeratTable(newId)

    # テーブルのID を引数に，そのテーブルの客を一人削除する
        # tableId : int : テーブルのID(配列のインデックス)
    def eliminateCustomeratTable(self, tableId):
        # 選択したテーブルの客を適当に探してきて削除
        for i in range(len(self.customers)):
            if self.customers[i] == tableId:
                self.customers.pop(i)
                break
        # 削除後のそのテーブルの客数を確認
        # ゼロ人ならそのテーブルを削除
        if self.getNumofCustomersofTable(tableId) == 0:
            w = self.tables[tableId]
            self.tables.pop(tableId)
        # テーブルを削除したなら，親店の対応する代理客を削除する
            if self.parent is not None:
                self.parent.eliminateCustomeratWord(w)
        # テーブルを削除したなら，全客に対して以下を行う
            for i in range(len(self.customers)):
        #   テーブル番号が削除したテーブル以上の客のインデックスを1減らす
                if self.customers[i] > tableId:
                    self.customers[i] = self.customers[i] - 1
        # 客が一人もいなくなった場合，親店にこの店の削除を要求する
            if len(self.customers) == 0 and self.parent is not None:
                self.parent.eliminateChild(self.getU()[0])
    # 相対文脈を引数に，子店を削除する
    # 客がなくなった子店側からの要求のために使用する 
        # u : str : 相対文脈．通常はすぐ下の子店からのみ要求を受けるはず
    def eliminateChild(self, u):
        if u in self.childs.keys():
            del self.childs[u]
        else:
            print("[Restaurant]eliminateChild:no child has context " + str(u))

    # 料理を引数に，その料理のおかれたテーブルのいずれかに客を一人追加する
    # 現段階では料理一種につきテーブル一つなので成立する
        # w : str : 料理
    def addCustomeratWord(self, w):
        flag = False
        newId = -1
        for i in range(len(self.tables)):
            if self.tables[i] == w:
                newId = i
                flag = True
                break
        # 指定した料理のテーブルがない場合は新設する
        if flag == False:
            newId = self.addNewTable(w)
            # 新設した場合，親店へ代理客を送る
            if self.parent is not None:
                self.parent.addCustomeratWord(w)
        self.addCustomeratTable(newId)

    # 料理を引数に，その料理のおかれたテーブルのいずれかの客を一人削除する
    # 現段階では料理一種につきテーブル一つなので成立する
        # w : str : 料理
    def eliminateCustomeratWord(self, w):
        for i in range(len(self.tables)):
            if self.tables[i] == w:
                self.eliminateCustomeratTable(i)
                return
        # 指定した料理のテーブルが存在しない場合，何もしない
        print("[Restaurant]eliminateCustomeratWord:no tables serving " \
         + str(w) + " in context " + str(self.getU()))   
 
    # 引数に与えた料理を提供するテーブルを新設する
        # w      : str : 料理
        # return : int : 新設されたテーブルの番号
    def addNewTable(self, w):
        self.tables.append(w)
        return len(self.tables)  - 1

    # （相対的な）文章(文脈 + 料理)を引数に，客を追加，
    # 子店がない場合は生成するメソッド
    # 下の getChildofForrowedU と混同しないように注意
        # u : list : 文章（文脈 + 料理） 最後の要素を料理として扱う
    def addCustomerfromSentence(self, u):
        # もし u が配列ならそのまま使う
        if isinstance(u, list):
            U = u
        # もし u が文字列なら，要素一つの配列に変える
        elif isinstance(u, str) == True:
            U = []
            U.append(u)
        # 文字列でも配列でもないときは間違いなのでエラー終了
        else:
            print("[Restaurant]addCustomerfromSentence:invalid inputs")
            return False

        # 一つの文章から，開始位置によって多数の文脈を取得できる
        # 根店の場合のみ，多数の開始位置に対応する再帰を行う
        if self.parent is None and len(U) >= 2:
            rec = self.addCustomerfromSentence(U[:-1])
            if rec == False:
                print("[Restaurant]addCustomerfromSentence:error")
                return False
        # 文脈長さが TERMINAL の場合，その文脈は無視する
        if len(self.getU()) >= TERMINAL:
            return True
        # U から「自分の文脈 + 料理」を除いた部分が「さらに深いngram」
        # なので，次の文脈を取得する
        # 文脈 + 料理 の長さが与えられた文章以上ならそれが最も深い文脈
        # 最も深い文脈である場合，料理に対応するテーブルに客を配置する
        if len(self.getU()) + 1 >= len(U):
            self.addCustomeratWord(U[-1])
            return True
        # 1個目の -1 は調整用，2個目は料理分を表す
        nextU = U[-1-1-len(self.getU())]
        # 対応する子店が存在しない場合，子店を生成する
        if nextU not in self.childs.keys():
            self.childs[nextU] = Restaurant(self,[nextU]+self.getU())
        # 子店に対して再帰的に関数を呼ぶ
        # self.addCustomeratWord(nextU)
        return self.childs[nextU].addCustomerfromSentence(U)

    # 文脈を引数に，その文脈の子店のオブジェクトを返す
    # その文脈のオブジェクトが存在しない場合は None を返す
    # →存在しない場合，新設するように変更．
    # 確率計算の際に未学習の文脈に遭遇することはあるため
    # 外部から叩く場合は根店限定
        # u      : list   : 文脈
        # return : object : 指定した文脈の子店
    def getChildofForrowedU(self, u):
        # もし u が配列ならそのまま使う
        if isinstance(u, list):
            U = u
        # もし u が文字列なら，要素一つの配列に変える
        elif isinstance(u, str) == True:
            U = []
            U.append(u)
        # 文字列でも配列でもないときは間違いなのでエラー終了
        else:
            print("[Restaurant]getChildofForrowedU:invalid inputs")
            return None
        # U が自分の文脈と同じなら自分を返す
        # 文脈が TERMINAL 以上ならそこが終端なので自分を返す
        if U == self.getU() or len(self.getU()) >= TERMINAL:
            return self
        else:
        # より深い適切な子店を取得する
            nextU = U[-1-len(self.getU())]
            # 適切な子店が存在しない場合，エラーを返す
            # →存在しない場合，新設するよう変更
            if nextU not in self.childs.keys():
                self.childs[nextU] = Restaurant(self,[nextU]+self.getU()) 
            return self.childs[nextU].getChildofForrowedU(U)
    # デバッグ用．ステータス表示
    def toPrint(self, t=0):
        tab = ""
        for i in range(t):
            tab = tab + "\t"
        print(tab + "====")
        # 文脈を表示
        print(tab + "U : " + str(self.u))
        # テーブルの状態を表示する
        print(tab + "T : " + str(self.tables))
        # 客の状態を表示する
        print(tab + "W : ")
        line = ""
        for i, c in enumerate(self.customers):
            line = line + self.tables[c] + ","
            if (i+1)%10 == 0:
                print(line)
                line = ""
        print(tab + line)
        print(tab + "====")
        
        for c in self.childs:
            self.childs[c].toPrint(t+1)

    # デバッグ用．疑似 json 出力
    def toJSON(self):
        output = {}
        output["U"] = self.getU()
        output["T"] = set(self.tables)
        childs_dict = {}
        for c in self.childs:
            childs_dict[c] = self.childs[c].toJSON()
        output["C"] = childs_dict
        return output 

    # 料理を引数に，その料理のおかれているテーブルの数を返す
    # 現段階ではt_uw = 1 なので0 or 1 を返す
        # w      : str : 料理
        # return : int : その料理のあるテーブルの数
    def getNumberofTablesofWord(self, w):
        output = 0
        for t in self.tables:
            if t == w:
                output = output + 1
        return output

    # テーブルのID を引数に，そのテーブルに座る客の数を返す
        # tableId : int : テーブルID (配列のインデックス)
        # return  : int : そのテーブルに座る客の数
    def getNumofCustomersofTable(self, tableId):
        output = 0
        for c in self.customers:
            if c == tableId:
                output = output + 1
        return output

    # 料理を引数に，その料理を食べる客の数を返す
    # 現段階では t_uw = 1 を仮定してるので，適切にテーブルを選べば上と同じ値になる
        # w      : str : 料理
        # return : int : その料理を提供してるテーブルに座る客の数の合計
    def getNumofCustomersofWord(self, w):
        output = 0
        for i in range(len(self.tables)):
            if self.tables[i] == w:
                output = output + self.getNumofCustomersofTable(i)
        return output

    # 単語を引数に，その店（文脈）および親店での確率を評価して返す
        # w : str  : 料理
    # テスト成功確認次第仮置きじゃなくす
    def calcProbabilityofForrowedU(self, w):
        # 計算に必要な値を用意する
            # この店の文脈 u で料理 w が生成された回数
        c_uw = self.getNumofCustomersofWord(w)
            # この店の文脈 u での全客数
        c_u = len(self.customers) 
            # この店の文脈 u で料理 w のおいてあるテーブルの個数
        t_uw = self.getNumberofTablesofWord(w)
            # この店の文脈 u での全テーブル数
        t_u = len(self.tables)
            # θ, d を求めておく
        theta = self.getTheta()
        d     = self.getD()
            # 親店での確率
            # 根店の場合は基底測度から取得
            # 根店には全料理が存在するはず
        Pdash = 0
        if self.parent is None:
            Pdash = self.calcProbabilityofBaseMeasure(w)
        else:
            Pdash = self.parent.calcProbabilityofForrowedU(w)
        # -------------------------------------------
        # 確率を計算する
        term1 =  (1.0*(c_uw - d*t_uw)) / (theta + c_u)
        term2 = ((1.0*(theta + d*t_u)) / (theta + c_u)) * Pdash
        return term1 + term2

    # 単語を引数に，基底測度から確率を評価して返す
    # 根店限定のメソッド
        # w : str : 料理
    def calcProbabilityofBaseMeasure(self, w):
        # 各単語等確率
        # output = 1.0/len(set(self.tables))
        # 長い単語ほど低確率
        a = paramA
        # output = (a)/(len(w) + a)
        output = np.exp(-len(w) * a)
        return output

    # 一文を引数に，その文章の生成確率を返す
    # そのまま計算するとかなり確率が小さくなってしまう気がするが，とりあえずそのまま計算する
    def calcProbability(self, sentence):
        # このメソッドは根店限定なので，根店以外で呼ばれていたら終了する
        if self.parent is not None:
            return -1
        output = 1
        tempUandW = []
        while tempUandW != sentence:
            # 計算対象の単語と文脈を更新
            tempUandW.append(sentence[len(tempUandW)])
            # 計算を行う文脈の店を取得する
            chi = self.getChildofForrowedU(tempUandW[:-1])
            # 確率を反映
            output = output * chi.calcProbabilityofForrowedU(tempUandW[-1])
            
        return output

    # 文章を引数に，その文章で追加された客を除去する
    def eliminateCustomerfromSentence(self, u):
        # もし u が配列ならそのまま使う
        if isinstance(u, list):
            U = u
        # もし u が文字列なら，要素一つの配列に変える
        elif isinstance(u, str) == True:
            U = []
            U.append(u)
        # 文字列でも配列でもないときは間違いなのでエラー終了
        else:
            print("[Restaurant]eliminateCustomerfromSentence:invalid inputs")
            return False

        # 一つの文章から，開始位置によって多数の文脈を取得できる
        # 根店の場合のみ，多数の開始位置に対応する再帰を行う
        if self.parent is None and len(U) >= 2:
            rec = self.eliminateCustomerfromSentence(U[:-1])
            if rec == False:
                print("[Restaurant]elminateCustomerfromSentence:error")
                return False
        # TERMINAL 以上の長さの文脈は無視する
        if len(self.getU()) >= TERMINAL:
            return True
        # U から「自分の文脈 + 料理」を除いた部分が「さらに深いngram」
        # なので，次の文脈を取得する
        # 文脈 + 料理 の長さが与えられた文章以上ならそれが最も深い文脈
        # 最も深い文脈である場合，料理に対応するテーブルに客を配置する
        if len(self.getU()) + 1 >= len(U):
            self.eliminateCustomeratWord(U[-1])
            return True
        # 1個目の -1 は調整分，2個目は料理分を表す
        nextU = U[-1-1-len(self.getU())]
        # 対応する子店が存在しない場合，子店を生成する
        if nextU not in self.childs.keys():
            self.childs[nextU] = Restaurant(self,[nextU]+self.getU())
        # 子店に対して再帰的に関数を呼ぶ
        return self.childs[nextU].eliminateCustomerfromSentence(U)

    # 文章と番号を引数に，指定した番号の場所の境界状態を入れ替える
    # 境界なら連結し，境界でないなら分割する
    def changeBoundary(self, u, idx):
        output = []
        temp = 0
        temp2 = ""
        flag = False
        for w in u:
            # 文字数を取得し，累積する
            temp = temp + len(w)
            # 境界操作後は残りの単語を取得するだけ
            if flag == True:
                output.append(w)
            elif temp2 != "":
                output.append(temp2 + w)
                flag = True
            # 指定文字数に到達していない場合，境界操作はまだ
            elif temp < idx+1:
                output.append(w)
            # 指定文字数と等しくなった場合，その次の境界を消す
            elif temp == idx+1:
                temp2 = w
            # 指定文字数を上回った場合，境界を作り分割する
            elif temp > idx+1:
                b = idx - (temp - len(w)) + 1
                output.append(w[:b])
                output.append(w[b:])
                flag = True
        # 連結用の単語が待機 and flag == False なら
        # 終端を連結しようとしているため，改めて append 
        if flag == False and temp2 != "":
            output.append(temp2)
        return output

    # 文章を引数に，境界状態をサンプリングする
        # u : list : 文章．
        # すでにモデルに反映されていることを前提とする(eliminate するため)
    def sampling(self, u):
        # u をモデルから eliminate
        self.eliminateCustomerfromSentence(u)
        # 以下を，u の境界候補全体で繰り返す
        newU = copy.deepcopy(u)
        print("[Restaurant]sampling:start " + str(newU) + "!!!")
        length = 0
        for w in u:
            length = length + len(w)
        for idx in range(length):
            # 境界部分を変更するほうとしないほうで確率計算
            newU_changed = self.changeBoundary(newU, idx)
            # 求めた確率をもとにサンプリング
            p_b = self.calcProbability(newU)
            p_a = self.calcProbability(newU_changed)
            if random.random() < p_a / (p_a + p_b):
                newU = newU_changed
        # 全境界候補にサンプリングを適用し，完成した文章をモデルに代入
        self.addCustomerfromSentence(newU)
        print("[Restaurant]sampling:get " + str(newU) + "!!!")
        # 終了
        return newU 

    # --------------------------------------------------------------------
    # 以下仮置きメソッド．順次実装


    # 文章の組（配列）を引数に，繰り返し学習して形態素解析の結果を返す
        # sentences : list(list) : 文章(単語の配列)の配列
        # iteration : int        : 再帰回数
    def executeParsing(self, sentences, iteration):
        # 根店以外で呼び出された場合は無効
        if self.parent is not None:
            return None
        currentSentences = copy.deepcopy(sentences)
        # 辞書が代入されることを想定してるので，
        # リストだった場合は適当な辞書に変更する
        if isinstance(currentSentences, list) == True:
            dic = {}
            for i in range(len(currentSentences)):
                dic[str(i)] = currentSentences[i]
            currentSentences = dic
        # 最初に，文章全てをモデルに代入する
        for s in currentSentences:
            self.addCustomerfromSentence(currentSentences[s])
        for idx in range(iteration):
            # 順番に代入しなおす(ギブスサンプリング)
            oldSentences = copy.deepcopy(currentSentences)
            for i in currentSentences:
                currentSentences[i] = self.sampling(currentSentences[i])
                # currentSentences[i] = self.blockedSampling(currentSentences[i])
            # 定期的に途中状態を表示してみる
            diff = self.compareParsing(oldSentences, currentSentences)
            print("[Restaurant]executeParsing:diff-" + str(diff))
            with open("tmp/Restaurant_executeParsing_diff_nonblock.txt", "a", encoding="utf-8") as f:
                f.write(str(diff) + "\n")
            if (idx) % 100 == 0 and idx != 0:
                print("[Restaurant]executeParsing:iteration:"+\
                str(idx))
                print("[Restaurant]executeParsing:currentSentences:")
                for s in currentSentences:
                    print(s + ":" + str(currentSentences[s]))
        # 最終結果を表示する
        print("[Restaurant]executeParsing:results:")
        for s in currentSentences:
            print(s + ":" + str(currentSentences[s]))
        return currentSentences

    # 数字をアルファベットに変換
    # 数字の列じゃダメだったのに今気づいた
    def translate(self, number):
        idx = number
        if number >= 58:
            idx = -1*(idx-58)
        """
        elif number >= 26:
            idx = idx + 6
        """
        return (chr(ord("A")+idx))

    # アルファベットを数字に変換
    def retranslate(self, alphabet):
        output = ord(alphabet) - ord("A")
        if output < 0:
            output = output * -1 + 58
        """
        if output >= 26:
            output = output - 6
        """
        return output

    # ブロック化サンプリング
    def blockedSampling(self, u):
        print("[Restaurant]blockedSampling:start " + str(u) + "!!!")
        # u をモデルから eliminate
        self.eliminateCustomerfromSentence(u)
        # u を全連結
        conc = ""
        for w in u:
            conc = conc + w
        # u の長さの3次元配列 a を作る
        a = []
        for _1 in range(len(conc)):
            a.append([])
            for _2 in range(len(conc)):
                a[-1].append([0 for _3 in range(len(conc))])
        # a を計算
        for t in range(len(conc)):
            if t == 0:
                a[0][0][0] = 1
            for k in range(t+1):
                for j in range(t-k+1):
                    sigma = 0
                    for i in range(t-k-j+1):
                        word1 = conc[t-k+1:t+1]
                        word2 = conc[t-k-j+1:t-k+1]
                        word3 = conc[t-k-j-i+1:t-k-j+1]
                        s = [word3, word2, word1]
                        if a[t-k][j][i] != 0:
                            # prob = self.calcProbability(s)
                            # 計算を行う文脈の店を取得する
                            chi = self.getChildofForrowedU(s[:-1])
                            # 確率を反映
                            prob = chi.calcProbabilityofForrowedU(s[-1])
                            sigma = sigma + prob*a[t-k][j][i]
                    a[t][k][j] = sigma
        # a をもとに分割を取得
        newU = []
        while True:
            if len(conc) <= 0:
                break
            B = []
            for k in range(len(conc)):
                B.append(sum(a[len(conc)-1][k]))
            rand = sum(B) * random.random()
            temp = 0
            select = -1
            for i, b in enumerate(B):
                temp = temp + b
                if temp > rand:
                    select = i
                    break
            newU = [conc[-1*select:]] + newU
            conc = conc[:-1*select]
        print("[Restaurant]blockedSampling:get " + str(newU) + "!!!")
        # 完成した文章をモデルに代入
        self.addCustomerfromSentence(newU)
        # 終了
        return newU 

    # 解析を比較する
    def compareParsing(self, before, after):
        output = 0
        # 各文に対して以下を行う
        # 1. 長く残っている方から最初の単語を取り除く
        #    同じ長さなら両方から取り除く
        # 2. 残りの長さの差を output にインクリメント
        # 3. 残りがなくなるまで繰り返す
        for k in before.keys():
            blist = before[k]
            alist = after[k]
            bconc = ""
            for b in blist:
                bconc = bconc + b
            aconc = ""
            for a in alist:
                aconc = aconc + a
            while True:
                if bconc == "" and aconc == "":
                    break
                if len(bconc) == len(aconc):
                    bconc = bconc[len(blist[0]):]
                    blist = blist[1:]
                    aconc = aconc[len(alist[0]):]
                    alist = alist[1:]
                elif len(bconc) > len(aconc):
                    bconc = bconc[len(blist[0]):]
                    blist = blist[1:]
                elif len(bconc) < len(aconc):
                    aconc = aconc[len(alist[0]):]
                    alist = alist[1:]
                else:
                    print("何かがおかしいよ")
                    exit()
                output = output + np.abs(len(bconc)-len(aconc))
        return output


if __name__ == "__main__" :
    rest = Restaurant(None, [])

    data = {}
    data["1"] = ["applegrapeorangebananapeach"]
    data["2"] = ["peachorangebananaapplegrape"]
    data["3"] = ["grapebananaorangeapplepeach"]
    data["4"] = ["bananaappleorangepeachgrape"]
    data["5"] = ["orangepeachbananaapplegrape"]

    rest.executeParsing(data, 10000)
    exit()

    # u = ["生きてることがつらいなら"]
    # rest.addCustomerfromSentence(u)
    u = ["生きてる", "ことがつらいなら"]
    rest.addCustomerfromSentence(u)
    u = ["生きてる", "ことが", "つらいなら"]
    rest.addCustomerfromSentence(u)
    u = ["生きて", "る", "ことが", "つらいなら"]
    rest.addCustomerfromSentence(u)
    print(rest.calcProbability(["生きてることがつらいなら"]))
    print(rest.calcProbability(["生きてる", "ことがつらいなら"]))
    print(rest.calcProbability(["生きてることが", "つらいなら"]))
    print(rest.calcProbability(["生きてる", "ことが", "つらいなら"]))
    print(rest.calcProbability(["生きてる", "ことが", "つらい", "なら"]))
    print(rest.calcProbability(["生き", "て", "る", "ことが", "つらい", "なら"]))

