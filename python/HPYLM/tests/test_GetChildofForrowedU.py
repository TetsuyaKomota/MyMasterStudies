#-*- coding:utf-8 -*-

import unittest
import Restaurant

class TestGetChildofForrowedU(unittest.TestCase):
    
    def test_getChildofForrowedU(self):
        
        # 根店を生成
        rest = Restaurant.Restaurant(None, [])
        # 文脈を適当に挿入
        u = ["今日", "も", "また", "人が", "死んだよ"]
        result = rest.getChildofForrowedU(u).getU()
        expected = u
        self.assertEqual(expected, result)

if __name__ == "__main__":
    unittest.main()
