#-*- coding:utf-8 -*-

# http://www.sas.com/offices/asiapacific/japan/service/technical/faq/list/body/stat034.html

import numpy as np
import random
import matplotlib.pyplot as plt

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
	means = [[0, 0], [-10, -10], [5, 10]]
	sigmas = [[[1, 0], [0, 1]], [[1, 0.5], [0.5, 1]], [[3, 2], [2, 1]]]
	rates = [0.3, 0.4, 0.3]
	size = 10000

	data = getData(c, means, sigmas, rates, size)

	print(data)

	# 描画しよう
	fig = plt.figure()
	ax = fig.add_subplot(1,1,1)
	pi = 0
	for i in range(c):
		n = int(size*rates[i])
		ax.scatter(data[pi:pi+n][0], data[pi:pi+n][1], s=20*i, label=str(i))
		pi = pi + n
	ax.set_xlabel('x')
	ax.set_ylabel('y')

	ax.grid(True)

	ax.legend(loc='upper left')
	fig.show()
