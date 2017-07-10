from gensim.models import word2vec
import MeCab
import dill
import numpy as np

if __name__ == "__main__":
    model = word2vec.Word2Vec.load("../../..//w2vModel/sample.model")

    m = MeCab.Tagger()
    namemap = {}
    with open("pokemon.csv", "r", encoding="utf-8") as f:
        line = f.readline()
        while line != "":
            namemap[line.split(",")[0]] = line.split(",")[4]
            line = f.readline()

    with open("type_names_dict.dill", "rb") as f:
        datas = dill.load(f)
    print(datas)

    vecs = {}
    for t in datas:
        vecs[t] = []
        for i in datas[t]:
            tempvec = np.zeros(200)
            texts = m.parse(namemap[i]).split("\n")
            for n in texts:
                tempn = n.split(",")
                if len(tempn) < 2:
                    break
                if tempn[6] != "*":
                    key = tempn[6]
                else:
                    key = tempn[0].split("\t")[0]
                try:
                    tempvec = tempvec + model[key]
                except KeyError:
                    print(key + " is not in model")
            vecs[t].append(tempvec)
    print(vecs)
    with open("type_vecs_dict.dill", "wb") as f:
        dill.dump(vecs, f)
