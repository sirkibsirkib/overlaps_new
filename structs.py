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


class Mappings:
	def __init__(self, id2names, id2index, index2len, index2id):
		self.id2names = id2names
		self.id2index = id2index
		self.index2len = index2len
		self.index2id = index2id