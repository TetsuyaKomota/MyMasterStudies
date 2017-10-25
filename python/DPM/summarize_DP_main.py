# coding = utf-8

import dill
import matplotlib.pyplot as plt

def run(path = "tmp/summarize_DP_main/img.png"):
        if isinstance(path, list):
            imgpath  = "tmp/MAINNOSYUUKEISURUNODA_results/"
            imgpath += "-".join([str(d) for d in path])
            imgpath += ".png"
        else:
            imgpath = path
        with open("tmp/log_MakerMain/dills/DP_main_temp.dill", "rb") as f:
            d = dill.load(f)

        matchList = d["matching"]
        print("[summarize_DP_main]num of matching:" + str(len(matchList)))       
 
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

if __name__ == "__main__":
    run()
