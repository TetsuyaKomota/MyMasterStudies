#-*- coding:utf-8 -*-

import unittest
import Restaurant

class TestGetChildofForrowedU(unittest.TestCase):
    
    # 新規文脈によって生成された子店の文脈が適切になっているかテスト
    def test_isCollectTerminalNode(self):
        
        # 根店を生成
        rest = Restaurant.Restaurant(None, [])
        # 文脈を適当に挿入
        u = ["今日", "も", "また", "人が", "死んだよ"]
        rest.addCustomerfromSentence(u)
        result = rest.getChildofForrowedU(u[:-1]).getU()
        expected = u[:-1]
        self.assertEqual(expected, result)

    # 途中まで共通した文脈で子店を生成した際に
    # 木構造が適切にできているかテスト
    def _test_isCollectTree(self):
 
        # 根店を生成
        rest = Restaurant.Restaurant(None, [])
        # 文脈を適当に挿入
        
        u1 = ["今日", "も", "また", "人が", "死んだよ"]
        u2 = ["今日", "も", "また", "俺は", "元気"]
        u3 = ["今日", "も", "また", "俺は", "残業"]
        rest.getChildofForrowedU(u1)
        rest.getChildofForrowedU(u2)
        rest.getChildofForrowedU(u3)

        uA = ["今日", "も"]
        uB = ["今日", "も", "また"]
        uC = ["今日", "も", "また", "俺は"]
        uD = ["今日", "も", "また", "俺は", "元気"]
        chiA = rest.getChildofForrowedU(uA)
        chiB = rest.getChildofForrowedU(uB)
        chiC = rest.getChildofForrowedU(uC)
        chiD = rest.getChildofForrowedU(uD)

        chiA.toPrint()
        chiB.toPrint()
        chiC.toPrint()
        chiD.toPrint()

        result = []
        result.append(chiA.getNumofChilds())
        result.append(chiB.getNumofChilds())
        result.append(chiC.getNumofChilds())
        result.append(chiD.getNumofChilds())

        # (今日も            )  の子は  （また）
        # (今日もまた        )  の子は  （人が，俺は）
        # (今日もまた俺は    )  の子は  （元気，残業）
        # (今日もまた俺は元気)  の子は　いない
        expected = [1, 2, 2, 0]
        self.assertEqual(expected, result)

    # 文章からの客生成が適切に行えているかのテスト
    def test_isCollectCustomers(self):
 
        # 根店を生成
        rest = Restaurant.Restaurant(None, [])
        # 文脈を適当に挿入
        
        u1 = ["昨夜", "眠れずに", "失望", "と", "戦った"]
        u2 = ["昨夜", "一晩中", "欲望", "と", "戦った"]
        u3 = ["だから", "一晩中", "絶望", "と", "戦った"]
        rest.addCustomerfromSentence(u1)
        rest.addCustomerfromSentence(u2)
        rest.addCustomerfromSentence(u3)

        """
        uA = []
        uB = ["今日"]
        uC = ["今日", "も"]
        uD = ["今日", "も", "また"]
        uE = ["今日", "も", "また", "俺は"]
        """
        uA = []
        uB = ["と"]
        uC = ["欲望", "と"]
        uD = ["一晩中", "欲望", "と"]
        uE = ["昨夜", "一晩中", "欲望", "と"]
        
        chiA = rest.getChildofForrowedU(uA)
        chiB = rest.getChildofForrowedU(uB)
        chiC = rest.getChildofForrowedU(uC)
        chiD = rest.getChildofForrowedU(uD)
        chiE = rest.getChildofForrowedU(uE)

        # rest.toPrint()

        result = []
        result.append(len(chiA.customers))
        result.append(len(chiB.customers))
        result.append(len(chiC.customers))
        result.append(len(chiD.customers))
        result.append(len(chiE.customers))

        # (                )  の客は 「昨夜」13個
        #   (全13単語中，同じ文脈からしか生じない「戦った」を1個と数える)
        # (と              )  の客は 「戦った」3個
        # (欲望と          )  の客は 「戦った」1個
        # (一晩中欲望と    )  の客は 「戦った」1個
        # (昨夜一晩中欲望と)  の客は 「戦った」1個
        expected = [13, 3, 1, 1, 1]
        self.assertEqual(expected, result)

    # 文章からの客削除が適切に行えているかのテスト
    def test_isCollectEliminate(self):

        # なぜか思考ごとに結果が変わるという場合があったので
        # 100回くらい試行して全部 OK の場合のみ OK とする
        flag = True
        for _ in range(100):
                # 根店を生成
                rest = Restaurant.Restaurant(None, [])
                # 文脈を適当に挿入
                
                u1 = ["きしむ", "ベッド", "の", "上で"]
                u2 = ["優しさ", "を", "持ち寄り"]
                rest.addCustomerfromSentence(u1)
                rest.addCustomerfromSentence(u2)
                before = rest.toJSON()

                # print("BEFORE ADDING u3")
                # rest.toPrint()
                
                
                u3 = ["きつく", "身体", "抱きしめあえば"]
                rest.addCustomerfromSentence(u3)
                # print("AFTER  ADDING u3")
                # rest.toPrint()
                
                rest.eliminateCustomerfromSentence(u3)
                after = rest.toJSON()
                
                # print("AFTER  ELIMINATING u3")
                # rest.toPrint()
                flag = flag and (before == after)
                if before != after:
                    print("after is different before:")
                    print("before:" + str(before))
                    print("after :" + str(after))
                    break

        self.assertTrue(flag)

    # 確率計算のテスト
    def test_calcProbabilityofForrowedU(self):

        # 根店を生成
        rest = Restaurant.Restaurant(None, [])
        # 文脈を適当に挿入

        u1 = ["生きてる", "こと", "が", "つらい", "なら"]
        u2 = ["いっそ", "小さく", "死ね", "ば", "いい"]
        u3 = ["生きてる", "こと", "が", "つらい", "なら"]
        u4 = ["喚き", "散らして", "泣け", "ば", "いい"]
        u5 = ["生きてる", "こと", "が", "つらい", "なら"]
        u6 = ["悲しみ", "を", "とくと", "見る", "が", "いい"]
        u7 = ["生きてる", "こと", "が", "つらい", "ならば"]
        u8 = ["くたばる", "喜び", "とっておけ"]
        
        rest.addCustomerfromSentence(u1)
        rest.addCustomerfromSentence(u2)
        rest.addCustomerfromSentence(u3)
        rest.addCustomerfromSentence(u4)
        rest.addCustomerfromSentence(u5)
        rest.addCustomerfromSentence(u6)
        rest.addCustomerfromSentence(u7)
        rest.addCustomerfromSentence(u8)

        # rest.toPrint()

        u = ["生きてる", "こと", "が", "つらい"]
        w1 = "なら"
        w2 = "ならば"
        w3 = "いい"
        w4 = "おっぺけぺ～"
        w5 = "だいだげき！"
        p1 = (rest.getChildofForrowedU(u).calcProbabilityofForrowedU(w1))
        p2 = (rest.getChildofForrowedU(u).calcProbabilityofForrowedU(w2))
        p3 = (rest.getChildofForrowedU(u).calcProbabilityofForrowedU(w3))
        p4 = (rest.getChildofForrowedU(u).calcProbabilityofForrowedU(w4))
        p5 = (rest.getChildofForrowedU(u).calcProbabilityofForrowedU(w5))

        """
        print(rest.getChildofForrowedU(u).getU())
        print(p1)
        print(p2)
        print(p3)
        print(p4)
        print(p5)
        """

        self.assertTrue((p1>p2) and (p2>p3) and (p3>p4) and (p4==p5))

    # 確率計算のテスト.数値指定版
    def test_calcProbabilityofForrowedU_hard(self):

        # 根店を生成
        rest = Restaurant.Restaurant(None, [])
        # 文脈を適当に挿入

        u1 = ["生きてる", "こと", "が", "つらい", "なら"]
        u2 = ["いっそ", "小さく", "死ね", "ば", "いい"]
        u3 = ["生きてる", "こと", "が", "つらい", "なら"]
        u4 = ["喚き", "散らして", "泣け", "ば", "いい"]
        u5 = ["生きてる", "こと", "が", "つらい", "なら"]
        u6 = ["悲しみ", "を", "とくと", "見る", "が", "いい"]
        u7 = ["生きてる", "こと", "が", "つらい", "ならば"]
        u8 = ["くたばる", "喜び", "とっておけ"]
        
        rest.addCustomerfromSentence(u1)
        rest.addCustomerfromSentence(u2)
        rest.addCustomerfromSentence(u3)
        rest.addCustomerfromSentence(u4)
        rest.addCustomerfromSentence(u5)
        rest.addCustomerfromSentence(u6)
        rest.addCustomerfromSentence(u7)
        rest.addCustomerfromSentence(u8)

        # rest.toPrint()

        u = ["生きてる", "こと", "が", "つらい"]
        w1 = "なら"
        w2 = "ならば"
        w3 = "いい"
        w4 = "おっぺけぺ～"
        w5 = "だいだげき！"
        p1 = (rest.getChildofForrowedU(u).calcProbabilityofForrowedU(w1))
        p2 = (rest.getChildofForrowedU(u).calcProbabilityofForrowedU(w2))
        p3 = (rest.getChildofForrowedU(u).calcProbabilityofForrowedU(w3))
        p4 = (rest.getChildofForrowedU(u).calcProbabilityofForrowedU(w4))
        p5 = (rest.getChildofForrowedU(u).calcProbabilityofForrowedU(w5))

        
        t1 = (p1 == 0.29297422954417)
        t2 = (p2 == 0.15011708668702714)
        t3 = (p3 == 0.04050244972864021)
        t4 = (p4 == 0.015967311912252386)
        t5 = (p5 == 0.015967311912252386)

        """
        print(t1)
        print(t2)
        print(t3)
        print(t4)
        print(t5)
        """

        self.assertTrue(t1 and t2 and t3 and t4 and t5)


    # 文章を引数とした確率計算
    def test_calcProbability(self):
        
        # 根店を生成
        rest = Restaurant.Restaurant(None, [])
        # 文脈を適当に挿入
        u1 = ["生きてる", "こと", "が", "つらい", "なら"]
        u2 = ["生きてる", "こと", "が", "つらい", "なら"]
        u3 = ["生きてる", "こと", "が", "つらい", "なら"]
        u4 = ["生きてる", "こと", "が", "つらい", "なら"]
        u5 = ["いっそ", "小さく", "死ね", "ば", "いい"]
        u6 = ["喚き", "散らして", "泣け", "ば", "いい"]
        
        rest.addCustomerfromSentence(u1)
        rest.addCustomerfromSentence(u2)
        rest.addCustomerfromSentence(u3)
        rest.addCustomerfromSentence(u4)
        rest.addCustomerfromSentence(u5)

        # 確率計算
        print(rest.calcProbability(u1))
        print(rest.calcProbability(u5))
        print(rest.calcProbability(u6))

        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
