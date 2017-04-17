import sys
		
def isPrime(num):
	for j in xrange(2, int(num ** (0.5))+1):
		if(num % j == 0):
			return False
	return True
lst = []
f = open("prime.log", "a")
try:
	for i in xrange(long(sys.argv[1]), long(sys.argv[2])):
		if(isPrime(i)):
			#print i
			lst.append(i)
			f.write(str(i) + "\n")
except:
	i = long(sys.argv[1])
	while i < long(sys.argv[2]):
		if(isPrime(i)):
			lst.append(i)
			#print i
			f.write(str(i) + "\n")
		i += 1
print lst
f.close()