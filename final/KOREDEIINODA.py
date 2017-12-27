import GenerateModelwithMakerMotions as generator
import EncodeModelwithSOINN as encoder
import ParsingModelwithNPYLM as parser
import PrunningModel as prunner
# import MatchingModelwithNN as matcher

if __name__ == "__main__":

    params = {}
    params["step"]     = [3, 5, 7]
    params["soinnN"]   = [3000, 5000000]
    params["soinnE"]   = [3000, 5000000]
    params["LEN"]      = [2, 5, 100]
    params["PAR_iter"] = [20, 200, 2000]
    params["MAT_iter"] = [1, 10, 100]

    idxs = {}
    for pName in params.keys():
        idxs[pName] = 0

    while True:

        p = {}
        for pName in params.keys():
            p[pName] = params[pName][idxs[pName]]

        dillpath = ""
        for pName in sorted(list(p.keys())):
            dillpath += pName + "="
            dillpath += str(p[pName]) + ","
        dillpath = dillpath[:-1] + "/"

        step        = p["step"]
        soinnN      = p["soinnN"]
        soinnE      = p["soinnE"]
        LEN         = p["LEN"]
        PAR_iter  = p["PAR_iter"]
        MAT_iter  = p["MAT_iter"]
     
        print("+--------")
        # generator.generate("tmp/log/", 100)
        print("++-------")
        # generator.generate("tmp/log_test/", 10)
        print("+++------")
        encoder.predict(dillpath, "tmp/log/", step, soinnN, soinnE)
        print("++++-----")
        encoder.predict(dillpath, "tmp/log_test/", step, soinnN, soinnE)
        print("+++++----")
        parser.parsing(dillpath, "encoded.dill", LEN, PAR_iter)
        print("++++++---")
        parser.parsing(dillpath, "encoded_test.dill", LEN, PAR_iter)
        print("+++++++--")
        prunner.prunning(dillpath)
        print("++++++++-")
        # matcher.matching(dillpath, MAT_iter) 
        print("+++++++++")

        flg = True
        for pName in params.keys():
            idxs[pName] += 1
            if idxs[pName] < len(params[pName]):
                flg = False
                break
            else:
                idxs[pName] = 0
        if flg == True:
            break
