# coding = utf-8

import dill
import matplotlib.pyplot as plt
import numpy as np

# マッチングのサマライズする
# ヒストグラムの作成と，F 値を算出して csv に追記するまで

def run(path = "tmp/summarize_DP_main/img.png"):
        # パラメータを - で連結して出力のファイル名を作る
        if isinstance(path, list):
            imgpath  = path[0]
            imgpath += "-".join([format(d, ".3f") for d in path[1:]])
            imgpath += ".png"
        else:
            imgpath = path
        with open("tmp/log_MakerMain/dills/DP_main_temp.dill", "rb") as f:
            d = dill.load(f)

        # ヒストグラムを求める
        matchList = d["matching"]
        print("[summarize_DP_main]num of matching:" + str(len(matchList)))       

        # after の step のヒストグラムを求めてたが，
        # matching ごとの after の step の平均でいいのでは？ 
        """
        alist = []
        for m in matchList:
            alist.append([a["step"] for a in m["after"]])

        total = sum([len(a) for a in alist])

        plt.xlim(0,500)
        I = 5
        j = 0
        for i in range(I):
            temp = []
            L = int(total/I)
            while True:
                if len(temp) >= L or j == len(alist):
                    break
                temp += alist[j]
                j += 1
            if len(temp) == 0:
                continue
            plt.hist(temp, bins = int((max(temp)-min(temp))/4))
        plt.savefig(imgpath)
        plt.close()
       
        """
        alist = []
        for m in matchList:
            alist.append([a["step"] for a in m["after"]])
            l = len(alist[-1])
            s = sum(alist[-1])
            alist[-1] = s/l

        plt.xlim(0,500)
        plt.hist(alist, bins = 250)
        plt.savefig(imgpath)
        plt.close()

        # F 値を求める
        # 各マッチングの step の平均を求め，100n と一致しているか判定する
        # 誤差はとりあえず適当に決める
        meanList = []
        for m in matchList:
            tempList = [a["step"] for a in m["after"]]
            meanList.append(sum(tempList)/len(tempList))

        stepRange = 30
        succ_p    = 0  # meanList のうち，100n と一致した個数
        succ_r    = 0  # 100n のうち，一致する meanList の存在した個数
        temp_r    = [False, False, False, False] # 一致した 100n のリスト
        for m in meanList:
            for r in range(len(temp_r)):
                if np.abs(m-100*(r+1)) <= stepRange:
                    succ_p += 1
                    temp_r[r] = True
        succ_r = sum([1 for t in temp_r if t==True])

        precision = (1.0*succ_p)/len(meanList) 
        recall    = (1.0*succ_r)/len(temp_r)
        if precision + recall == 0:
            f_score = 0
        else:
            f_score   = 2.0/((1.0/precision) + (1.0/recall))

        # csv に追記
        with open(path[0] + "result.csv", "a", encoding="utf-8") as f:
            text  = imgpath[:-4] + ","
            text += str(precision) + ","
            text += str(recall)    + ","
            text += str(f_score)   + "\n"
            f.write(text)

if __name__ == "__main__":
    run()
