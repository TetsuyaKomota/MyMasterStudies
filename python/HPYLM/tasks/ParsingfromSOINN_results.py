#-*- coding: utf-8 -*-

import Restaurant
import RefactedRestaurant
import dill
import sys, io


# def execute(paramA=5, paramTheta=1.0, paramNumS=0, paramNumT=1, reverse=False):
def execute(D=1, A=5, Theta=1.0, PAD=1, hpylm_iter=1000, reverse=False):
    # sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    print("Start Parsing Test (from tmp/SOINN_results.dill)")

    # rest = Restaurant.Restaurant(None, [], paramA = paramA, paramTheta = paramTheta, paramNumS=paramNumS, paramNumT=paramNumT)
    rest =RefactedRestaurant.Franchise(D, A, Theta, PAD, 2)

    # with open("tmp/HMM_results.dill", "rb") as f:
    with open("tmp/log_MakerMain/dills/SOINN_results.dill", "rb") as f:
        datas = dill.load(f)
        elis = []
        for d in datas:
            if "000" not in d:
                elis.append(d)
        for e in elis:
            del datas[e]
    u = {}
    for d in datas:
        print(datas[d])
        line = ""
        for s in datas[d]:
            line = line + rest.translate(s)
        # u.append([line])
        u[d] = [line]
    print("input sentences:")
    for s in u:
        print(u[s][0])

    result = rest.executeParsing(u, hpylm_iter)
    if reverse == True:
        result_rev = rest.executeParsing(u, hpylm_iter, reverse=True)
        for s in result_rev:
            result[s + str("_rev")] = result_rev[s]

    print("parsing results:")
    for r in result:
        line = ""
        for w in result[r]:
            line = line + w + ", "
        print(line)

    with open("tmp/log_MakerMain/dills/HPYLM_results.dill", "wb") as f:
        dill.dump(result, f)
        print("Successfully dumping : result")

if __name__ == "__main__":
    execute(paramTheta = 5.0)
