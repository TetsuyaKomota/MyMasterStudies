# -*- coding: utf-8 -*-

import numpy as np
import warnings
import dill
import glob
from hmmlearn import hmm

import MakeData

"""
2017/ 7/1
通常の HMM を用いて符号化を行う実験用のコード
学習に使う時系列データは MakeData.py で生成
"""

# テスト関数

class MyHMM:

    def __init__(self, num):
        self.n_components = num

    # とりあえず試してみるだけの奴．
    def experiment_0(self, detail=False):

        # datas = MakeData.make2()

        methods = []
        methods.append(MakeData.make1)
        methods.append(MakeData.make2)
        # methods.append(MakeData.make3)
        # methods.append(MakeData.make4)

        dataList = []
        for m in methods:
            # とりあえず各軌道2回ずつ取得して学習データに使う
            for _ in range(2):
                dataList.append(m())

        lengths = []
        for d in dataList:
            lengths.append(len(d))

        datas = np.concatenate(dataList)

        # MakeData.showData(datas, detail)

        model = hmm.GaussianHMM(n_components=self.n_components, covariance_type="full")    
        
        # model.fit(datas)
        model.fit(datas, lengths)
        
        # 学習結果を表示
        if detail == True:
            print("startprob_")
            print(model.startprob_)
            print("means_")
            print(model.means_)
            print("covars_")
            print(model.covars_)
            print("transmat_")
            print(model.transmat_)    

        # 推定．連続する同状態はカットして，遷移の様子だけ取り出す
        pre = model.predict(datas)
        result = []
        for p in pre:
            if len(result) == 0 or p != result[-1]:
                result.append(p) 
        if detail == True:
            print("dataList:")
            print(result)

        # 学習したモデルをもとに，推定を行う
        # dill 出力して，それをHPYLM で参照する
        results = {}
        for i, m in enumerate(methods):
            print("MakeData.make" + str(i+1) + ":")
            results_temp = []
            for _ in range(10):
                pre = model.predict(m())
                result = []
                for p in pre:
                    if len(result) == 0 or p != result[-1]:
                        result.append(p) 
                if detail == True:
                    print(result)
                results_temp.append(result)
            results["make"+str(i+1)] = results_temp
        with open("tmp/HMM_results.dill", "wb")  as f:
            dill.dump(results, f)
            print("Successfully dumping")
    
    # Makedata ではなく with open から動くタイプ
    # tmp/log_makeMain 直下のログデータをすべて使って学習して符号化する
    # 生成するdill は以下の二つ
    #   ・通常の符号列
    #   ・遷移部分を抽出せずに長いままの符号列
    # これらは辞書として生成し，同じキーを保ち，ログファイル名と関連付けておく
    def experiment_1(self, detail=False):

        filenames = glob.glob("tmp/log_MakerMain/*")
        print(filenames)
        dataList  = []
        fnameList = [] # dill する辞書のキーに使うファイル名
        for fname in filenames:        
            # csv 以外は無視
            if fname[-4:] != ".csv":
                continue
            # fnameList を作る
            fnameList.append(fname[-12:-4])
            # ログを読み込む
            with open(fname, "r", encoding="utf-8") as f:
                tempdata = []
                while(True):
                    # [1:-1] はステップ番号と改行文字を無視する為
                    # line = f.readline().split(",")[1:-1]
                    line = f.readline().split(",")[1:3]
                    if len(line) < 2:
                        break
                    tempdata.append(np.array([float(x) for x in line]))
                dataList.append(tempdata)
        # 一旦確認
        print(dataList[0])
        print(fnameList[0])

        lengths = []
        for d in dataList:
            lengths.append(len(d))

        datas = np.concatenate(dataList)

        model = hmm.GaussianHMM(n_components=self.n_components, covariance_type="full")    
        
        model.fit(datas, lengths)
        
        # 学習結果を表示
        if detail == True:
            print("startprob_")
            print(model.startprob_)
            print("means_")
            print(model.means_)
            print("covars_")
            print(model.covars_)
            print("transmat_")
            print(model.transmat_)    

        # 学習したモデルをもとに，推定を行う
        # dill 出力して，それをHPYLM で参照する

        results       = {}
        results_naive = {}
        for i, d in enumerate(dataList):
            result       = []
            result_naive = []
            pre = model.predict(d)
            for p in pre:
                result_naive.append(p)
                if len(result) == 0 or p != result[-1]:
                    result.append(p)
            if detail == True:
                print(result)
            results[fnameList[i]]       = result
            results_naive[fnameList[i]] = result_naive
        with open("tmp/log_MakerMain/dills/HMM_results.dill", "wb")  as f:
            dill.dump(results, f)
            print("Successfully dumping : results")
        with open("tmp/log_MakerMain/dills/HMM_results_naive.dill", "wb")  as f:
            dill.dump(results_naive, f)
            print("Successfully dumping : results_naive")



if __name__ == "__main__":
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = MyHMM(30)
        model.experiment_1(True)
