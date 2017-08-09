#-*- coding:utf-8 -*-

import unittest
import Restaurant

class TestTERMINAL(unittest.TestCase):
   
    @classmethod 
    def setUpClass(self):
        self.rest = Restaurant.Restaurant(None, [])
        u1 = ["昨夜", "眠れずに", "失望", "と", "戦った"]
        u2 = ["昨夜", "一晩中", "欲望", "と", "戦った"]
        u3 = ["だから", "一晩中", "絶望", "と", "戦った"]
        self.rest.addCustomerfromSentence(u1)
        self.rest.addCustomerfromSentence(u2)
        self.rest.addCustomerfromSentence(u3)

    # rest.toPrint()

    def test_isSameBaseRestaurant(self):
        self.assertEquals(self.rest.getNumofChilds(), 8)
    """
    全然分からん
    def test_isLimited(self):
        check = True
        for c in self.rest.childs:
            if check == False:
                break
    """     

if __name__ == "__main__":
    unittest.main()
