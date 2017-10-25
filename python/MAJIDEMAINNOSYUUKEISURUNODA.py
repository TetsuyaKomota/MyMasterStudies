# coding = utf-8
import dill
import DPM.ViewPointManager as manager
import DPM.predictMatching as matching
import DPM.summarize_DP_main as summarizer
import glob
from ParamManager import ParamManager
from ParamManager import NOPARAMS

def run():
    print("start MAINSYU")
    filepaths = glob.glob("tmp/log_MakerMain/*")
    dirname   = "100-0-3-2000-0.01-0.11-0.02-5-False-500"
    # データ取得
    datas = manager.getStateswithViewPoint(filepaths, [], [])
    pm = ParamManager("MAINSYU")
    p  = pm.firstParams()

    count = 0
    while True:
        print("[MAINSYU]iteration:" + str(count))
        count += 1
        if p == NOPARAMS:
            break
        print("---------- : make DP_main_results.dill")
        with open("tmp/log_MakerMain/dills/DP_main_results.dill", "wb") as f:
            interdict = matching.getInterDict(dirname)
            dill.dump(matching.DP_main(datas, interdict, \
                sampleSize=pm.pick(p, "sampleSize"), \
                n_iter=pm.pick(p, "n_iter"),\
                distError=pm.pick(p, "distError")), f)
        print("+++++----- : save Histogram as png")
        summarizer.run([p[name] for name in pm.getParamNameList()])
        print("++++++++++ : Finished")
        p = pm.nextParams()

if __name__=="__main__":
    run()
