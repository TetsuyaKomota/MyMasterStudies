# coding = utf-8

# 乱択などを一切行っていないと思えるプログラムが
# 実行するたびに結果が変わる事態が生じたので
# それらに関してのテストコード

import unittest
import DPM.ViewPointManager as manager
import glob
import numpy as np

class TestNonRandom(unittest.TestCase):

    # viewPointManager の getStatewithViewPoint は毎回同じ結果を返すか
    def test_ViewPointManager_getStatewithViewPoint(self):
        output = True
        filepaths = glob.glob("tmp/log_MakerMain/*")
        # データ取得
        datas = manager.getStateswithViewPoint(filepaths, [], [])
        for _ in range(3):
            temp = manager.getStateswithViewPoint(filepaths, [], [])
            for fname in datas:
                if len(datas[fname]) != len(temp[fname]):
                    output = False
                    break
                for i in range(len(datas[fname])):
                    for o in datas[fname][i]:
                        a = datas[fname][i][o]
                        b = temp[fname][i][o]
                        if type(a)==type(np.array([])):
                            output = output and (np.allclose(a, b))
                        else:
                            output = output and (a == b)
            if output == False:
                break
        self.assertTrue(output)

    def test_pick0and100(self):
        output = True
        filepaths = glob.glob("tmp/log_MakerMain/*")
        # データ取得
        datas = manager.getStateswithViewPoint(filepaths, [], [])
        stateDict = {}
        stateDict["before"] = []
        stateDict["after"]  = []
        for count, d in enumerate(datas):
            stateDict["before"].append(datas[d][0])
            stateDict["after"].append(datas[d][100])
            if count >= 49:
                break
        for _ in range(3):
            tempDict = {}
            tempDict["before"] = []
            tempDict["after"]  = []
            for count, d in enumerate(datas):
                tempDict["before"].append(datas[d][0])
                tempDict["after"].append(datas[d][100])
                if count >= 49:
                    break
            if len(stateDict["before"]) != len(tempDict["before"]):
                output = False
                break
            for i in range(len(stateDict["before"])):
                output = output and (stateDict["before"][i]["step"]==tempDict["before"][i]["step"])
            if output == False:
                break
        self.assertTrue(output)

if __name__ == "__main__":
    unittest.main()
