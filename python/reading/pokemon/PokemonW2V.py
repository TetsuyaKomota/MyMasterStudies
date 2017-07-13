from gensim.models import word2vec
import MeCab
import dill
import numpy as np


class W2V:
    def __init__(self):
        self.model = word2vec.Word2Vec.load("../../..//w2vModel/sample.model")
        self.m = MeCab.Tagger()

    def vectorize(self, sentence, detail=False):
        texts = self.m.parse(sentence).split("\n")
        tempvec = np.zeros(200)
        encoded = ""
        for n in texts:
            tempn = n.split(",")
            if len(tempn) < 2:
                break
            if tempn[0].split("\t")[1] not in ["名詞", "動詞", "形容詞"]:
                continue
            if tempn[6] != "*":
                key = tempn[6]
            else:
                key = tempn[0].split("\t")[0]
            encoded = encoded + key + ","
            try:
                tempvec = tempvec + self.model[key]
            except KeyError:
                print(key + " is not in model")
        if detail==True:
            print("ENCODED : " + encoded)
        return tempvec 


if __name__ == "__main__":

    namemap = {}
    with open("pokemon.csv", "r", encoding="utf-8") as f:
        line = f.readline()
        while line != "":
            namemap[line.split(",")[0]] = line.split(",")[4]
            line = f.readline()

    with open("type_names_dict.dill", "rb") as f:
        datas = dill.load(f)
    print(datas)

    w2v = W2V()

    vecs = {}
    for t in datas:
        vecs[t] = []
        for i in datas[t]:
            print(namemap[i])
            vecs[t].append(w2v.vectorize(namemap[i], detail=True))
    # print(vecs)
    with open("type_vecs_dict.dill", "wb") as f:
        dill.dump(vecs, f)
