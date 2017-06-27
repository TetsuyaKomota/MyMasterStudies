#-*- coding:utf-8 -*-

# HPYLM において各ノードにあたる「店」クラス

# ====================================================
# 定数
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
        return 10

    # 割引係数 d のゲッター
    def getD(self):
    # t_uw (店u で料理w のおいてあるテーブルの数=親店から取得した回数)はとりあえず1固定
    # つまりこれはPY ではなくIKN
       return 0.5

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
        if U == self.getU():
            return self
        else:
        # より深い適切な子店を取得する
            nextU = U[-1-len(self.getU())]
            # 適切な子店が存在しない場合，エラーを返す
            # →存在しない場合，新設するよう変更
            if nextU not in self.childs.keys():
                self.childs[nextU] = Restaurant(self,[nextU]+self.getU()) 
            return self.childs[nextU].getChildofForrowedU(U)
    """
    # （相対的な）文脈を引数に，子店を取得，ない場合は生成するメソッド
    def old_getChildofForrowedU(self, u):
        # もし u が空配列なら，自分を返す
        if isinstance(u, list) == True and len(u) == 0:
            return self
        # 一つの文章から，開始位置によって多数の文脈を取得できる
        # 根店の場合のみ，多数の開始位置に対応する再帰を行う
        if self.parent is None:
            self.getChildofForrowedU(u[1:])
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
        # もしU[0] を文脈とする子店がないなら，新規に作成する
        if U[0] not in self.childs.keys():
            self.childs[U[0]] = Restaurant(self, self.getU() + [U[0]])
        # 子供に対して再帰的に関数を呼ぶ
        return self.childs[U[0]].getChildofForrowedU(U[1:])
    """
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

    # 単語を引数に，その店（文脈）および親店での確率を評価して返す
        # w : str  : 料理
    # テスト成功確認次第仮置きじゃなくす
    def calcProbabilityofForrowedU(self, w):
        # -------------------------------------------
        # 指定した文脈にあたる店まで移動する
        # -------------------------------------------
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
            # 根店の場合はその店自体の全料理数の逆数(全料理等確率)
            # 根店には全料理が存在するはず
        Pdash = 0
        if self.parent is None:
            Pdash = 1.0/len(set(self.tables))
        else:
            Pdash = self.parent.calcProbabilityofForrowedU(w)
        # -------------------------------------------
        # 確率を計算する
        term1 =  (1.0*(c_uw - d*t_uw)) / (theta + c_u)
        term2 = ((1.0*(theta + d*t_u)) / (theta + c_u)) * Pdash
        return term1 + term2

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

    # --------------------------------------------------------------------
    # 以下仮置きメソッド．順次実装

    # 文章を引数に，その文章で追加された客を除去する
    # TODO まだ addCustomesfromSentence をコピペしただけ
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


