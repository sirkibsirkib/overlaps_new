cigar_code_invert = {'I':'D', 'M':'M', 'D':"I"}

class Cigar:
	def __init__(self, cigar_seq):
		self.cigar_seq = cigar_seq

	def h_flip(self):
		# before = str(self)
		self.cigar_seq = self.cigar_seq[::-1]
		# print(before, '--hflip-->', str(self))

	def v_flip(self):
		# before = str(self)
		self.cigar_seq = [(n, cigar_code_invert[code]) for (n, code) in self.cigar_seq]
		# print(before, '--vflip-->', str(self))

	def rotate(self):
		before = str(self)
		self.cigar_seq = [(n, cigar_code_invert[code], n) for (n, code) in self.cigar_seq][::-1]
		# print(before, '--rot-->', str(self))

	def __repr__(self):
		try:
			return ''.join([str(n) + code for (n, code) in self.cigar_seq])

		except:
			print(self.cigar_seq)
			raise

	def __lt__(self, other):
		return self.cigar_seq < other.cigar_seq

	def __eq__(self, other):
		return self.cigar_seq == other.cigar_seq

	def __hash__(self):
		return str(self).__hash__()

	def align(self, a, b):
		#a=from		b=to
		# print("  CIGAR BABY")
		# print(self.cigar_seq)
		# print('  a', a)
		# print('  b', b)
		# print('  cigar', self)
		# print('  len a', len(a))
		# print('  leb b', len(b))
		a_cigar = ''
		b_cigar = ''
		a_i = 0
		b_i = 0
		for n, code in self.cigar_seq:
			# print('code', '[' + code + ']')
			# print('n', '[' + str(n) + ']')
			if code == 'I':
				for _ in range(int(n)):
					a_cigar += '-'
					b_cigar += b[b_i]
					b_i += 1
			elif code == 'D':
				for _ in range(int(n)):
					b_cigar += '-'
					a_cigar += a[a_i]
					a_i += 1
			else:
				for _ in range(int(n)):
					a_cigar += a[a_i]
					a_i += 1
					b_cigar += b[b_i]
					b_i += 1
		# print('  aligned: ', a_cigar, b_cigar)
		return a_cigar, b_cigar

def cigar_for_match_of_len(length):
	return Cigar([(length,'M')])

def cigar_sequence(cigar_str):
	cig = cigar_str
	seq = []
	while len(cig) > 0:
		num_len = 0
		while cig[:num_len+1].isdigit():
			num_len += 1
		n = int(cig[:num_len])
		code = cig[num_len]
		cig = cig[num_len + 1:]
		seq.append((n, code))
	print(cigar_str, '==>', seq)
	return seq

# def v_flip_cigar(cigar):
# 	flipped =  ''.join([str(n) + cigar_code_invert[code] for n, code in cigar_sequence(cigar)])
# 	print(cigar, '=v_flip=>', flipped)
# 	return flipped
#
#
# def rotate_cigar(cigar):
# 	rotated = ''
# 	for n, code in cigar_sequence(cigar):
# 		rotated = str(n) + code + rotated
# 	print(cigar, '=rot=>', rotated)
# 	return rotated
#
# def h_flip_cigar(cigar):
# 	flip = ''
# 	for n, code in cigar_sequence(cigar):
# 		flip = str(n) + code + flip
# 	print(cigar, '=h_flip=>', flip)
# 	return flip

# def align_using_cigar(a, b, cigar):
# 	print("\nCIGAR BABY")
# 	print('a', a)
# 	print('b', b)
# 	print('cigar', cigar)
# 	print('len a', len(a))
# 	print('leb b', len(b))
# 	a_cigar = ''
# 	b_cigar = ''
# 	a_i = 0
# 	b_i = 0
# 	for n, code in cigar_sequence(cigar):
# 		print('code', '[' + code + ']')
# 		print('n', '[' + str(n) + ']')
# 		if code == 'I':
# 			for _ in range(int(n)):
# 				a_cigar += '-'
# 				b_cigar += b[b_i]
# 				b_i += 1
# 		elif code == 'D':
# 			for _ in range(int(n)):
# 				b_cigar += '-'
# 				a_cigar += a[a_i]
# 				a_i += 1
# 		else:
# 			for _ in range(int(n)):
# 				a_cigar += a[a_i]
# 				a_i += 1
# 				b_cigar += b[b_i]
# 				b_i += 1
# 	return a_cigar, b_cigar