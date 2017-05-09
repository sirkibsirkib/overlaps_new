import random
import time
X = 8
from itertools import accumulate

def cand(z, filter, err, forwards=True):
	err_cnt = 0
	if forwards:
		for index in range(z, X):
			err_cnt += err[index]
			if err_cnt > filter[index-z]:
				return index
	else:
		for index in range(z, -1, -1):
			err_cnt += err[index]
			if err_cnt > filter[index]:
				return index
	return -1



err  = [0 for _ in range(X)]
for i in range(X-1):
	ind = random.randint(0, X-1)
	err[ind] += 1

print('   ', err)
print('cumulative...')
print('-->', list(accumulate(err)))
print('   ', list(accumulate(err[::-1]))[::-1], '<--')
print()
filters = []
for z in range(X):
	res = dict()
	p = False
	if z < X/2 or True:
		filter = [i for i in range(0, X-z)]
		falls_off = cand(z, filter, err, forwards=True)
		r = 'ACCEPT' if falls_off==-1 else falls_off
		print(z, '>>', '   '*z+ str(filter), '  ', r)

	else:
		filter = [i for i in range(0, z+1)][::-1]
		falls_off = cand(z, filter, err, forwards=False)
		r = 'ACCEPT' if falls_off==-1 else falls_off
		print(z, '  ', str(filter)+'   '*(X-z-1), '<<', r)
print('                        ^index where filter failed')