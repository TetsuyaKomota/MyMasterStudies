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
        result = rest.getChildofForrowedU(u).getU()
        expected = u
        self.assertEqual(expected, result)

    # 途中まで共通した文脈で子店を生成した際に
    # 木構造が適切にできているかテスト
    def test_isCollectTree(self):
 
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

if __name__ == "__main__":
    unittest.main()
