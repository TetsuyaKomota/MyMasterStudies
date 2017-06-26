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


if __name__ == "__main__":
    unittest.main()
