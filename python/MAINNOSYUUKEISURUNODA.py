# coding = utf-8
import dill
import DPM.ViewPointManager as manager
import DPM.predictMatching as matching
import DPM.summarize_DP_main as summarizer
import glob

filepaths = glob.glob("tmp/log_MakerMain/*")
# データ取得
datas = manager.getStateswithViewPoint(filepaths, [], [])
 
sampleSize = 0.0
for _1 in range(10):
    sampleSize += 0.1
    n_iter = 0
    for _2 in range(6):
        n_iter += 50
        distError = 5
        for i in range(5):
            distError /= 10
            with open("tmp/log_MakerMain/dills/DP_main_results.dill", "wb") as f:
                dill.dump(matching.DP_main_2(datas, matching.getInterDict("3-2500-2500-11-5-1"), sampleSize=sampleSize, n_iter=n_iter, distError=distError), f)
            summarizer.run("tmp/MAINNOSYUUKEISURUNODA_results/"+str(sampleSize)+"-"+str(n_iter)+"-5e-"+str(i+1)+".png")
