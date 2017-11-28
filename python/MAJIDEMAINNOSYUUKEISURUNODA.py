# coding = utf-8
import dill
import DPM.ViewPointManager as manager
import DPM.predictMatching as matching
import DPM.summarize_DP_main as summarizer
import DPM.result_kireinisuruyatsu as kirei
import glob
import os
from ParamManager import ParamManager
from ParamManager import NOPARAMS

DIR_PATH = "tmp/MAJIDEMAINNOSYUUKEISURUNODA_results/"

def run():
    if os.path.exists(DIR_PATH) == False:
        os.mkdir(DIR_PATH)
    print("start MAINSYU")
    filepaths = glob.glob("tmp/log_MakerMain/*")
    dirname   = "3-2000-10-0.11-200-5-5-False-100"
    # dirname   = "CHEATNANODA_results"
    # データ取得
    datas = manager.getStateswithViewPoint(filepaths, [], [])
    pm = ParamManager("MAINSYU")
    pm.printREADME("MAINSYU")
    p  = pm.firstParams()
    paramNum = len(p)

    count = 0
    while True:
        print("[MAINSYU]iteration:" + str(count))
        count += 1
        if p == NOPARAMS:
            break
        print("---------- : make DP_main_results.dill")
        with open("tmp/log_MakerMain/dills/DP_main_results.dill", "wb") as f:
            # 指定したディレクトリの境界情報を取得
            interdict = matching.getInterDict(dirname)
            interdict = matching.pruningInterDict(interdict)
            dill.dump(matching.DP_main(datas, interdict, \
                sampleSize=pm.pick(p, "sampleSize"), \
                n_iter=pm.pick(p, "n_iter"),\
                distError=pm.pick(p, "distError")), f)
        print("+++++----- : save Histogram as png")
        summarizer.run([DIR_PATH] + [p[name] for name in pm.getParamNameList()])
        print("++++++++++ : Finished")
        p = pm.nextParams()
    # kirei で result.csv を p, r, f に集計
    for y in range(paramNum):
        for x in range(y):
            kirei.execute(x, y)

if __name__=="__main__":
    run()
