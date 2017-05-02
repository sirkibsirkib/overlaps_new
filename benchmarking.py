import time


class Benchmarker:
	def __init__(self):
		self.times = [time.clock()]

	def time(self, prompt):
		time_now = time.clock()
		delta = time_now - self.times[len(self.times)-1]
		print('>> TIME TAKEN FOR #{} "{}" : {:4f} sec.'.format(len(self.times)-1, prompt, delta))
		self.times.append(time_now)

	def total_time(self):
		print('>> TOTAL TIME TAKEN: {:4f} sec.'.format(self.times[len(self.times)-1] - self.times[0]))