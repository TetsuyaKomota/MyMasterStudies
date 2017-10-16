# coding = utf-8

import random

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

# 削除済みの要素(客，テーブル)を表す
DELETED = "THIS FACTOR HAVE DELETED"

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
        customerLIst = []
        tids = getTableListofWord(u, word)
        for tid in tids:
            customerList += self.countCustomersofTable(u, tid)
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
        CustomerList = self.getCustomerListofTable(u, tableId)
        if len(CustomerList) == 0:
            return
        delCustomer = CustomerList[0]
        rest[CUSTOMER][delCustomer] = DELETED
        # そのテーブルを生成した親文脈のテーブルから代理客を削除
        if len(u) > 0:
            pid = rest[TABLE][tableId][T_PID]
            self.eliminateCustomerofTable(u[1:], pid)

    # 文脈を取得する
    # 文脈がない場合は生成する
    def getRestaurant(self, u):
        self.addRestaurant(u)
        return self.restaurants[u]

    def addRestaurant(self, u):
        # 文脈が LEN より長い場合は生成しない
        if len(u) > self.LEN:
            return 
        # 文脈が存在しない，または DELETED なら新たに生成
        if u not in self.restaurants.keys() \
                or self.restaurants[u] == DELETED:
            self.restaurants[u] = [[], []]
 
    def eliminateRestaurant(self, u):
        self.restaurants[u] = DELETED

    # ピットマンヨー過程から，指定した単語のテーブルID を取得
    # 単語指定の条件付確率を用いる
    # 新テーブルが選択される場合は NEW を返す
    def pickwithPitmanYor(self, u, word):
        rest = self.getRestaurant(u)
        tableList = self.getTableListofWord(u, word)
        tableHist = {NEW:self.THETA}
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
    def  addSentence(self, sentence):
        part = [PADWORD for _ in range(self.LEN)]
        for word in sentence:
            part = part[1:] + [word]
            # すべてパディングであるような文脈は無視
            if part == [PADWORD for _ in range(self.LEN)]:
                continue
            print("added:" + str(part))
            self.addRestaurant(tuple(part[:-1]))
            self.addCustomerofWord(tuple(part[:-1]), part[-1])
            self.toPrint()
       
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


if __name__ == "__main__":
    f = Franchise(1, 1, 1, 1, 3)
    f.addSentence(["今日", "も", "また", "人", "が", "死んだよ"])
    f.addSentence(["今日", "も", "また", "雨", "が", "降ったよ"])
    f.toPrint()











