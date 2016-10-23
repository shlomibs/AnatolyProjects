#!/usr/bin/python
import sys
from sklearn import datasets, svm
import matplotlib.pyplot as plt
#import numpy as np

def lstToFloat(lst):
	finalStr = ""
	for i in lst:
		if float(i) < 10:
			finalStr += "0" + str(int(i));
		else:
			finalStr += i
	return int(finalStr)


data = open("Lotto.csv").read().replace("\r", "").split("\n")[1:-1]
dataTable = [i.split(",") for i in data]
#print data[0]
#print data[-1]

x = [(dataTable[i][0],dataTable[i][1].split("/")[0],dataTable[i][1].split("/")[1],dataTable[i][1].split("/")[2],dataTable[i + 1][-1], dataTable[i + 1][-2])
	for i in xrange(len(dataTable) - 1)]
y = [dataTable[i][2:-2] for i in range(len(dataTable) - 1)]
#print x[-1]

#lstToFloat = lambda lst: [float(i) for i in lst]

#x = [lstToFloat(i) for i in x]

y = [lstToFloat(i) for i in y]

#print x
#print y

clf = svm.SVC(gamma=0.001, C=100)

clf.fit(x[2:], y[2:]) # data, corresponding true result

print "data length: ", len(x[2:])

print "prediction: ", str(clf.predict(x[1])), "true: ", y[1]
print "prediction: ", str(clf.predict(x[0])), "true: ", y[0]











