#-*- coding:utf-8 -*-

# http://www.sas.com/offices/asiapacific/japan/service/technical/faq/list/body/stat034.html

import numpy as np
import random
import matplotlib.pyplot as plt
from time import sleep

def getData(c, means, sigmas, rates, size):

	output = []

	# クラスタ数 c と 平均、分散、混合比の数が一致してなければエラー
	if c != len(means) or c != len(sigmas) or c != len(rates):
		print("ERROR: invalid inputs")
		return output

	for i in range(c):
		# 混合比に応じた量のデータを生成
		n = int(size*rates[i])
		# 準備
		a = sigmas[i][0][1]/(sigmas[i][0][0]*sigmas[i][0][0])
		b = np.sqrt(sigmas[i][1][1]*sigmas[i][1][1] - ((sigmas[i][0][1]*sigmas[i][0][1])/(sigmas[i][0][0]*sigmas[i][0][0])))
		
		# 乱数生成
		for k in range(n):
			x = means[i][0] + sigmas[i][0][0] * random.random()
			y = means[i][1] + a * (x - means[i][0]) + b * random.random()
			output.append([x, y])
		#
	#
	return output

if __name__ == "__main__":
	c = 3
	means = [[0, 0], [-1, -1], [0.5, 1]]
	sigmas = [[[1, 0], [0, 1]], [[1, 0.5], [0.5, 1]], [[1, 0], [0, 2]]]
	rates = [0.3, 0.4, 0.3]
	size = 10000

	data = getData(c, means, sigmas, rates, size)

	print(data)

	# 描画しよう
	pi = 0
	for i in range(c):
		n = int(size*rates[i])
		print(n)
		# plt.scatter(data[pi:pi+n][0], data[pi:pi+n][1], s=20+10*i,color = [(np.sqrt(2)*i)%1, (np.sqrt(3)*i)%1, (np.sqrt(5)*i)%1],  label=str(i))
		pi = pi + n


	plt.scatter(data[0:3000][0], data[0:3000][1], s=20,color = [0,0,0],  label="1")
	plt.scatter(data[3000:7000][0], data[3000:7000][1], s=30,color = [0.5, 0.5, 0.5],  label="2")
	plt.scatter(data[7000:10000][0], data[7000:10000][1], s=40,color = [0.75, 0.75, 0.75],  label="3")


	plt.grid(True)

	plt.legend(loc='upper left')
	plt.show()
	sleep(3)
