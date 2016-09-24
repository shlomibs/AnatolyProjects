#!/usr/bin/python
import sys
from sklearn import datasets, svm
import matplotlib.pyplot as plt
#import numpy as np

digits = datasets.load_digits() # loads digits (partial or handwritten) images and the digits corresponding

clf = svm.SVC(gamma=0.001, C=100)

clf.fit(digits.data[:-10], digits.target[:-10]) # data, corresponding true result

inp = "1"
while True:
	inp = raw_input(">>> ")
	if inp == "exit": exit()
	print "prediction: ", str(clf.predict(digits.data[int(inp)])), "true: ", digits.target[int(inp)]
	plt.imshow(digits.images[int(inp)], cmap = plt.cm.gray_r, interpolation="nearest")
	plt.show()
