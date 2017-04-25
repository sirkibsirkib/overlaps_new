class Arguments:
	def __init__(self, indels=True, inclusions=True, inverts=True, e=0.02, thresh=20):
		self.indels = indels
		self.inclusions = inclusions
		self.inverts = inverts
		self.e = e
		self.thresh = thresh

	def __repr__(self):
		return ' indels {}\ninclusions {}\ninverts {}\ne {}\nthresh {}'\
			.format(self.indels, self.inclusions, self.inverts, self.e, self.thresh)