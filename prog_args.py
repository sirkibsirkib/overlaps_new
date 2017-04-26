class Arguments:
	def __init__(self, indels, inclusions, inverts, e, thresh, in_path, out_path):
		self.indels = indels
		self.inclusions = inclusions
		self.inverts = inverts
		self.e = e
		self.thresh = thresh
		self.in_path = in_path
		self.out_path = out_path

	def __repr__(self):
		return ' indels {}\ninclusions {}\ninverts {}\ne {}\nthresh {}\nin_path {}\nout_path {}'\
			.format(self.indels, self.inclusions, self.inverts, self.e, self.thresh, self.in_path, self.out_path)