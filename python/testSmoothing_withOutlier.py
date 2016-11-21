# -*- coding:utf-8 -*-
import matplotlib.pyplot as plt
import math
import random
'''
データの平滑化のテスト
単純な関数の形のデータ + 一様誤差 or 外れ値 という形の場合


'''



def getSMA(data, n, isHM):
	output = []

	buf = 0

	for idx in range(len(data)):
		buf = buf + data[idx]/n
		if idx >= n-1:
			output.append(buf)
			buf = buf - data[idx-(n-1)]/n

	return output

def getTMA(data, n, isHM):
	output = []
	output = getSMA(getSMA(data, math.ceil((n+1)/2), isHM), math.ceil((n+1)/2), isHM)
	return output

def getWMA(data, n, isHM):
	output = []

	total = 0
	numerator = 0

	for idx in range(len(data)):
		numerator = numerator + n*data[idx] - total
		total = total + data[idx]
		if idx >= n:
			total = total - data[idx-n]
		if idx >= n-1:
			output.append(numerator/(n*(n+1)/2))
	return output

def getEMA(data, n, isHM):
	output = []
	alpha = 2/(n+1)
	buf = 0

	for idx in range(len(data)):
		if idx < (n-1):
			buf = buf + data[idx]/n
		else:
			buf = (1-alpha)*buf + alpha*data[idx]
			output.append(buf)
	return output

if __name__ == "__main__":
	print("Hello world")
	data = []

	numofData = 300
	# l = 5
	l = 21
	L = 61
	randomRange = 1000000
	outlierRate = 0.1

	maxdata = 0
	mindata = 0

	for i in range(numofData):
		nextdata = (i*i*i - 450 *i*i + 60000 *i +100000) + randomRange * random.random()
		data.append(nextdata)
		if nextdata > maxdata:
			maxdata = nextdata
		if nextdata < mindata:
			mindata = nextdata

	# 外れ値の生成
	for i in range(len(data)):
		if random.random() < outlierRate:
			data[i] = (maxdata - mindata)*random.random() + mindata
			
	
	sldata = getSMA(data, l, False)
	sLdata = getSMA(data, L, False)
	wldata = getWMA(data, l, False)
	wLdata = getWMA(data, L, False)
	eldata = getEMA(data, l, False)
	eLdata = getEMA(data, L, False)
	tldata = getTMA(data, l, False)
	tLdata = getTMA(data, L, False)

	print("data :" , data)
	print("sldata:" , sldata)
	print("sLdata:" , sLdata)
	print("wldata:" , wldata)
	print("wLdata:" , wLdata)
	print("eldata:" , eldata)
	print("eLdata:" , eLdata)
	print("tldata:" , tldata)
	print("tLdata:" , tLdata)
	
	plt.plot(range(numofData), data, label="original")
	plt.plot(range(l-1, numofData), sldata, label="SMA_smallRange")
	plt.plot(range(L-1, numofData), sLdata, label="SMA_largeRange")
	plt.plot(range(l-1, numofData), wldata, label="WMA_smallRange")
	plt.plot(range(L-1, numofData), wLdata, label="WMA_largeRange")
	plt.plot(range(l-1, numofData), eldata, label="EMA_smallRange")
	plt.plot(range(L-1, numofData), eLdata, label="EMA_largeRange")
	plt.plot(range(l-1, numofData), tldata, label="TMA_smallRange")
	plt.plot(range(L-1, numofData), tLdata, label="TMA_largeRange")
	plt.legend(loc="upper left")
	plt.show()

