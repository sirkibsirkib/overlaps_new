import time


class Benchmarker:
	def __init__(self):
		self.new_log()

	def log_moment(self, prompt):
		entry = prompt, time.clock()
		self.log.append(entry)
		print('Logging moment at {:>14.5f}s : {}'.format(entry[1], entry[0]))

	def __repr__(self):
		s = 'BENCHMARKED MOMENTS:\nLOGGED (s)    \tDELTA (s)     \tPERCENT   \tPROMPT    \n'
		prev_time = self.log[0][1]
		total_time = self.log[-1][1] - self.log[0][1]
		for i, entry in enumerate(self.log[1:]):
			delta = entry[1] - prev_time
			perc = delta/total_time*100
			prev_time = entry[1]
			s += '{:>14.5f}\t{:>14.5f}\t{:>9.3f}%\t{}\n'.format(
				entry[1], delta, perc, entry[0])
		return s

	def new_log(self):
		self.log = [('started', time.clock())]