# coding = utf-8

import soundfile as sf
import numpy as np

datak, ratek = sf.read("tmp/full.wav")
datat, ratet = sf.read("tmp/tibetan.wav")

print(ratek)
print(ratet)


# けものフレンズの音声 4 分の 1 を学習
# そのあとはそれぞれ 10 等分にして挟む

spank = len(datak)
spant = len(datat)

data = []

data += list(datak[:int(spank/4)])
for i in range(10):
    data += list(datat[int(spant/10)*i:int(spant/10)*(i+1)])
    data += list(datak[int(spank/4)+int(spank*(3/40))*i:int(spank/4)+int(spank*(3/40))*(i+1)])

data = np.array(data)

sf.write("tmp/merged.wav", data, ratek)
