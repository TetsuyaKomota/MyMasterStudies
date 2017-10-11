#-*- coding: utf-8 -*-

import Restaurant
import dill
import sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def execute(paramA=5, paramTheta=1.0, paramNumS=0, paramNumT=1):
    print("Start Parsing Test (from tmp/SOINN_results.dill)")

    rest = Restaurant.Restaurant(None, [], paramA = paramA, paramTheta = paramTheta, paramNumS=paramNumS, paramNumT=paramNumT)

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
        """
        # 終端文字を加える
        line = line + "~"
        -> 終端文字ではなく終端単語を Restaurant の段階で加えるように変更
        """
        # u.append([line])
        u[d] = [line]
    print("input sentences:")
    for s in u:
        print(u[s][0])

    result = rest.executeParsing(u, 10000)

    """
    # results のすべての文の最後の単語に終端文字がついているはずなので
    # このタイミングで除去しておく
    for r in result:
        result[r][-1] = result[r][-1][:-1]

    -> 終端単語の除去も Restaurant でやってる
    """
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
