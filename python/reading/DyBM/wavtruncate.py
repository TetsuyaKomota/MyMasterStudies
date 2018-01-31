# coding = utf-8

import soundfile as sf

data, samplerate = sf.read("full.wav")

"""
for i in range(10):
    span = 10**5
    sf.write("truncate["+str(5*10**6+span*i)+"-"+str(5*10**6+span*(i+1))+"].wav", data[5*10**6+span*i:5*10**6+span*(i+1)], samplerate)
"""
b = 5330000
a = 5850000
sf.write("truncate["+str(b)+"-"+str(a)+"].wav", data[b:a], samplerate)
