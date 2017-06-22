#-*- coding:utf-8 -*-

# HPYLM において各ノードにあたる「店」クラス

# ====================================================
# 定数
    # PY過程における未知数の強度. ディリクレ過程における α
theta = 10
    # PY過程における割引率．上とともに本来はlen(u) によって決まる関数だが，
    # とりあえず簡単のために定数化
d     = 0.5
    # t_uw (店u で料理w のおいてあるテーブルの数=親店から取得した回数)はとりあえず1固定
    # つまりこれはPY ではなくIKN
t     = 1

class Restaurant:

    # u         : 文脈．店のインデックスと考えてもよい
    # parent    : 親店のオブジェクト
    # childs    : 子店のオブジェクトの辞書．キーを文脈の最後の単語（相対文脈）とする
    # customers : 客の配列
    def __init__(self, parent, u):
        self.parent = parent
        self.u = u
        self.tables    = []
        self.customers = []
        self.childs    = {}

    # 親店のゲッター
    def getParent(self):
        return self.parent

    # 文脈のゲッター
    def getU(self):
        return self.u

    # （相対的な）文脈を引数に，子店を取得，ない場合は生成するメソッド
    def getChildofForrowedU(self, u):
        # もし u が空配列なら，自分を返す
        if isinstance(u, list) == True and len(u) == 0:
            return self
        # もし u が配列ならそのまま使う
        elif isinstance(u, list):
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

    # 料理を引数に，その料理のおかれているテーブルの数を返す
    # 現段階ではt_uw = 1 なので0 or 1 を返す
        # w      : str : 料理
        # return : int : その料理のあるテーブルの数
    def getTuw(self, w):
        return 0

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
        return 0

    # 料理を引数に，この店（=文脈）でその料理（=単語）を観測する確率を返す
        # w      : str   : 料理（単語）
        # return : float : その単語がこの文脈で出現する確率
    def calcProbability(self, w):
        return 0.0
