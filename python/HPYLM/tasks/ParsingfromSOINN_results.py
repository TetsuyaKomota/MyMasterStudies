#-*- coding: utf-8 -*-

import Restaurant
import dill
import sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def execute(paramA = 5):
    print("Start Parsing Test (from tmp/SOINN_results.dill)")

    rest = Restaurant.Restaurant(None, [], paramA = paramA)

    # with open("tmp/HMM_results.dill", "rb") as f:
    with open("tmp/log_MakerMain/dills/SOINN_results.dill", "rb") as f:
        datas = dill.load(f)
        elis = []
        for d in datas:
            if "000000" not in d:
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

    result = rest.executeParsing(u, 10000)

    print("parsing results:")
    for r in result:
        line = ""
        for w in r:
            line = line + w + ", "
        print(line)

    with open("tmp/log_MakerMain/dills/HPYLM_results.dill", "wb") as f:
        dill.dump(result, f)
        print("Successfully dumping : result")

if __name__ == "__main__":
    execute()
