import dill
from sklearn import svm
import PokemonW2V
from datetime import datetime

from sklearn import cross_validation
from sklearn.cross_validation import cross_val_score

with open("type_vecs_dict.dill", "rb") as f:
    loaded = dill.load(f)

datas  = []
labels = []
idx_type_map = {}

for i, t in enumerate(loaded):
    idx_type_map[i] = t
    for v in loaded[t]:
        datas.append(v)
        labels.append(i)
print(datas)
print(labels)

clf = svm.SVC()
clf.fit(datas, labels)

w2v = PokemonW2V.W2V()

name_text_map = {}
name_type_map = {}
with open("pokemon.csv", "r", encoding="utf-8") as f:
    line = f.readline().split(",")
    while len(line) > 2:
        name_text_map[line[0]] = line[4]
        name_type_map[line[0]] = line[2]
        line = f.readline().split(",")

success = 0
count = 0
with open("result/resultSVM" + str(int(datetime.now().timestamp()))+".txt", "w", encoding="utf-8") as f:
    for n in name_text_map:
        predicted = idx_type_map[clf.predict(w2v.vectorize(name_text_map[n]))[0]]
        print(n + " : " + name_type_map[n] + " -> " + predicted)
        f.write(n + " : " + name_type_map[n] + " -> " + predicted + "\n")
        count = count + 1
        if predicted == name_type_map[n]:
            success = success + 1

    print(str(success) + "/" + str(count))
    f.write(str(success) + "/" + str(count)+"\n")

# leave-1-out で検定してみよう
scores = cross_validation.cross_val_score(clf, datas, labels, cv=5,)
print("scores: " + str(scores))
print("Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))
