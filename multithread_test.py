import random
import benchmarking
from multiprocessing import Pool

def work(arg):
	count = 0
	while count < 1000000:
		count += 1

def test(thread_count):
	benchmarker = benchmarking.Benchmarker()
	pool = Pool(thread_count)
	pool.map(work, range(100))
	benchmarker.log_moment('DONE!')
	print(benchmarker)

if __name__ == '__main__':
	for i in range(1, 12):
		print(i, '-->')
		test(i)