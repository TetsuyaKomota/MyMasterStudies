#-*- coding: utf-8 -*-

import dill
import Restaurant

# HPYLM_results.dill と ENC_results_naive.dill から，
# 単語境界のステップ数を取得する
def execute():
        # HPYLM の結果のパス
        RES_PATH_HPYLM     = "tmp/log_MakerMain/dills/HPYLM_results.dill"
        # 縮約前の ENC(HMM or SOINN) の符号化結果のパス
        # RES_PATH_ENC_NAIVE = "tmp/log_makerMain/dills/HMM_results_naive.dill"
        RES_PATH_ENC_NAIVE = "tmp/log_makerMain/dills/SOINN_results_naive.dill"

        # それぞれ読み込む
        with open(RES_PATH_HPYLM, "rb") as f:
            datas_HPYLM = dill.load(f)
        with open(RES_PATH_ENC_NAIVE, "rb") as f:
            datas_ENC_naive = dill.load(f)

        # ENC_results_naive.dill は数字列のままなので
        # Restaurant の translate を使って符号化する

        rest = Restaurant.Restaurant(None, [])
        u = {}
        for d in datas_ENC_naive:
            line = ""
            for s in datas_ENC_naive[d]:
                line = line + rest.translate(s)
            u[d] = line
        datas_ENC_naive = u

        # 境界部分のステップ番号のリストを作る
        output = {}

        for i, d in enumerate(datas_ENC_naive):
            print(d)
            m = [1]
            naive = datas_ENC_naive[d]
            sentence = datas_HPYLM[d]
            # print(naive)
            # print(sentence)
            step = 0
            for word in sentence:
                for c in word:
                    while True:
                        if step < len(naive) and naive[step] == c:
                            step = step + 1
                        else:
                            break
                m.append(step)
            output[d] = m
        # とりあえず表示してみる
        print(output)

        # dill.dump しておく
        with open("tmp/log_MakerMain/dills/Getting_intermediates_results.dill", "wb") as f:
            dill.dump(output, f)

        # log ファイルから境界ステップの情報だけを切り出した log データを作成
        for d in output:
            tempD = "log"+d[5:]
            with open("tmp/log_MakerMain/" + tempD + ".csv", "r") as f:
                tempD = "inter"+d[5:]
                with open("tmp/log_MakerMain/GettingIntermediated/" + tempD + ".csv", "w") as g:
                    for s in output[d]:
                        while True:
                            line = f.readline().split("\n")[0]
                            if line == "":
                                break
                            if line.split(",")[0] == str(s):
                                g.write(line + "\n")
                                break

if __name__ == "__main__":
    execute()
