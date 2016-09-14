f = lambda n: 1 if n==0 else n*f(n-1)	

if __name__ == "__main__":
	print str(f(input("number")))
	raw_input()