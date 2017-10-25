# coding = utf-8

import setting

NOPARAMS = "there is no paramater any more."
NAME     = 0
IDX      = 1

class ParamManager:
    def __init__(self, name="HONKORE"):
        if   name == "HONKORE":
            self.params  = setting.HONKORE_PARAMS
        elif name == "MAINSYU":
            self.params  = setting.MAINSYU_PARAMS
        self.counter = []

    def pick(self, paramList, key):
        # paramList のキーには自動割り振りの数字インデックスがついている
        # 利用時にそれがいくつかわからないため，キー名のみで指定できるように変更する
        for p in paramList.keys():
            if key in p:
                return paramList[p]
        return None

    def getParamNameList(self):
        return sorted(list(self.params.keys()))

    def firstParams(self):
        self.counter = [[p, 0] for p in self.params.keys()]
        output = {}
        for c in self.counter:
            output[c[NAME]] = self.params[c[NAME]][c[IDX]]
        return output

    def nextParams(self):
        return self.sub_nextParams(0)
 
    def sub_nextParams(self, i):
        # +1しても配列内に収まるなら
        if self.counter[i][IDX]+1<len(self.params[self.counter[i][NAME]]):
            self.counter[i][IDX] += 1
            output = {}
            for c in self.counter:
                output[c[NAME]] = self.params[c[NAME]][c[IDX]]
            return output
        # 収まらないなら
        else:
            if i >= len(self.counter)-1:
                return NOPARAMS
            self.counter[i][IDX] = 0
            return self.sub_nextParams(i+1)

    def printREADME(self):
        fpath = "tmp/log_MakerMain/GettingIntermediated/README.txt"
        with open(fpath, "w", encoding="utf-8") as f:
            f.write("ディレクトリのパラメータは以下の順に並んでいます\n")
            f.write(str(self.getParamNameList()))
            f.write("\n\n")
            f.write(setting.HONKORE_EXPLANATION)


