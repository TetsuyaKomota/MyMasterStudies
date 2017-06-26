#-*- coding:utf-8 -*-

# HPYLM において各ノードにあたる「店」クラス

# ====================================================
# 定数
class Restaurant:

    # u         : 文脈．店のインデックスと考えてもよい
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
        print(self.getU())

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

    # 引数に与えた料理を提供するテーブルを新設する
        # w : str : 料理
    def addNewTable(self, w):
        self.tables.append(w)

    # （相対的な）文脈を引数に，子店を取得，ない場合は生成するメソッド
    def getChildofForrowedU(self, u):
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


    # --------------------------------------------------------------------------------------
    # 以下仮置きメソッド．順次実装

    # テーブルのID を引数に，そのテーブルに客を一人追加する
        # tableId : int : テーブルのID(配列のインデックス)
    def addCustomeratTable(self, tableId):
        print("hogehoge")

    # 料理を引数に，その料理のおかれたテーブルのいずれかに客を一人追加する
    # 現段階では料理一種につきテーブル一つなので成立する
        # w : str : 料理
    def addCustomeratWord(self, w):
        print("hogehoge")

    # 料理を引数に，親店からその料理のテーブル新設を要求する
    # 親店にもない場合は再帰的に要求する
        # w : str : 料理
    def orderNewWord(self, w):
        print("hogehoge")

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
        return 0

    # 料理を引数に，その料理を食べる客の数を返す
    # 現段階では t_uw = 1 を仮定してるので，適切にテーブルを選べば上と同じ値になる
        # w      : str : 料理
        # return : int : その料理を提供してるテーブルに座る客の数の合計
    def getNumofCustomersofWord(self, w):
        output = 0
        for i in range(len(self.tables)):
            if self.tables[i] == w:
                for c in self.customers:
                    if c == i:
                        output = output + 1
        return output

    # 料理を引数に，この店（=文脈）でその料理（=単語）を観測する確率を返す
        # w      : str   : 料理（単語）
        # return : float : その単語がこの文脈で出現する確率
    def calcProbabilityforThis(self, w):
        return 0.0

    # 文脈と単語を引数に，その店および親店での確率を評価して返す
        # u : list : 文脈の配列
        # w : str  : 料理
    def calcProbability(self, u, w):
        # 計算に必要な値を用意する
            # 文脈 u で料理 w が生成された回数
        c_uw = self.getNumofCustomersofWord(w)
            # 文脈 u での全客数
        c_u = len(self.customers) 
            # 文脈 u で料理 w のおいてあるテーブルの個数
        t_uw = self.getNumberofTablesofWord(w)
            # 文脈 u での全テーブル数
        t_u = len(self.tables)
            # 親店での確率
            # 根店の場合はその店自体の全料理数の逆数(全料理等確率)
            # 根店には全料理が存在するはず
        Pdash = 0
        if self.parent is None:
            Pdash = 1.0/set(self.tables)
        else:
            Pdash = self.parent.calcProbability(u[1:], w)
        return 0.0        

