# coding = utf-8
# predictMatching で取得した観点列で実際に動作を再現してみる

import HDP_HMM.MakerMotions as motions
import DPM.ViewPointEncoder as encoder
import DPM.ViewPointManager as manager
import copy
import dill
import setting

def reproduction(initState, matchingDict):
    manager.show(initState)
    state = copy.deepcopy(initState)
    for vp in matchingDict["viewpoint"]:
        state = manager.predictwithViewPoint(state, vp)
        manager.show(state)

if __name__ == "__main__":
    with open("tmp/log_MakerMain/dills/DP_main_results.dill", "rb") as f:
        matchingDict = dill.load(f)
    initState = motions.getInits()
    initState["hand"] = [0.0, 0.0]
    initState["step"] = 0
    reproduction(initState, matchingDict)
